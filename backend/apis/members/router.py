from fastapi import APIRouter, HTTPException
from database import get_db_connection
from models import *

router = APIRouter()


@router.get("/api/members", response_model=List[MemberResponse], tags=["Members"])
def get_all_members():
    """
    Fetches a list of all members.
    LEFT JOIN ensures members without a plan are still shown (plan_name will be null).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.member_id, m.first_name, m.last_name, m.phone, m.join_date, m.status, mp.plan_name
        FROM members m
        LEFT JOIN membership_plans mp ON m.plan_id = mp.plan_id
        ORDER BY m.join_date DESC;
    """
    cursor.execute(query)
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return members


@router.patch("/api/members/{member_id}/status", tags=["Members"])
def update_member_status(member_id: int, status_data: UpdateMemberStatus):
    """Updates a specific member's status (e.g., freezing their account)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE members SET status = %s WHERE member_id = %s;", (status_data.status, member_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"Member {member_id} status updated to {status_data.status}"}


@router.get("/api/members/{member_id}/dashboard", response_model=MemberDashboard, tags=["Members"])
def get_member_dashboard(member_id: int):
    """
    Aggregates data for a member's profile page.
    Uses subqueries in the SELECT statement to efficiently calculate total paid and total visits.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            m.first_name || ' ' || m.last_name AS full_name,
            mp.plan_name,
            mp.duration_months,
            (SELECT SUM(amount) FROM payments WHERE member_id = m.member_id AND status = 'paid') AS total_paid,
            (SELECT COUNT(*) FROM attendance WHERE member_id = m.member_id) AS total_visits
        FROM members m
        JOIN membership_plans mp ON m.plan_id = mp.plan_id
        WHERE m.member_id = %s;
    """
    cursor.execute(query, (member_id,))
    dash = cursor.fetchone()
    cursor.close()
    conn.close()
    if not dash:
        raise HTTPException(status_code=404, detail="Member not found")
    return dash
