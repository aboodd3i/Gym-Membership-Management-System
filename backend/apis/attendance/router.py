from fastapi import APIRouter, HTTPException
from database import get_db_connection
from models import *

router = APIRouter()


@router.post("/api/attendance", tags=["Attendance"])
def record_check_in(checkin_data: CheckInRequest):
    """
    Records a member check-in. 
    DB handles default timestamp automatically.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO attendance (member_id) VALUES (%s);", (checkin_data.member_id,))
        conn.commit()
        return {"message": "Check-in recorded!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/api/attendance", response_model=List[AttendanceLogResponse], tags=["Attendance"])
def get_full_attendance_log():
    """Admin view: Full log of all check-ins across the gym."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT a.attendance_id, m.first_name || ' ' || m.last_name AS member, a.check_in
        FROM attendance a
        JOIN members m ON a.member_id = m.member_id
        ORDER BY a.check_in DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/attendance/most-active", response_model=List[MemberVisitCount], tags=["Attendance"])
def get_most_active_members():
    """Aggregates attendance to rank members by total visits."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.first_name || ' ' || m.last_name AS member,
               COUNT(a.attendance_id) AS total_visits
        FROM attendance a
        JOIN members m ON a.member_id = m.member_id
        GROUP BY m.member_id, m.first_name, m.last_name
        ORDER BY total_visits DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/attendance/lazy-members", response_model=List[LazyMemberResponse], tags=["Attendance"])
def get_lazy_members():
    """Finds members who pay but never show up (NOT IN subquery)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.first_name || ' ' || m.last_name AS member, u.email
        FROM members m
        JOIN users u ON m.user_id = u.user_id
        WHERE m.member_id NOT IN (
            SELECT DISTINCT member_id FROM attendance
        );
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/members/{member_id}/attendance", response_model=List[dict], tags=["Attendance"])
def get_member_attendance(member_id: int):
    """Member view: Fetches their personal check-in history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT check_in FROM attendance WHERE member_id = %s ORDER BY check_in DESC;", (member_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/attendance/today-count", tags=["Attendance"])
def get_todays_attendance_count():
    """Dashboard stat: How many people checked in today."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS check_ins_today FROM attendance" \
    " WHERE DATE(check_in) = CURRENT_DATE;")
    count = cursor.fetchone()
    cursor.close()
    conn.close()
    return count
