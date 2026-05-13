from fastapi import APIRouter, HTTPException
from database import get_db_connection
from models import *

router = APIRouter()


@router.post("/api/auth/login", response_model=LoginResponse, tags=["Authentication"])
def login_user(login_data: UserLogin):
    """
    Logs in a user by checking credentials.
    Uses LEFT JOIN so it works for Admins, Trainers, and Members.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query joins users with members and trainers to get role-specific IDs and names
    query = """
        SELECT u.user_id, u.role, u.password_hash,
               m.member_id, m.first_name AS member_first_name, m.last_name AS member_last_name,
               t.trainer_id, t.first_name AS trainer_first_name, t.last_name AS trainer_last_name
        FROM users u
        LEFT JOIN members m ON u.user_id = m.user_id
        LEFT JOIN trainers t ON u.user_id = t.user_id
        WHERE u.email = %s;
    """
    cursor.execute(query, (login_data.email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    # Basic validation (in production, use bcrypt to hash passwords!)
    if not user or user["password_hash"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    #if user['role'] != 'admin':
    #   raise HTTPException(status_code=403, detail="Access Denied. Admin portal only.")

    del user["password_hash"]
    return user
