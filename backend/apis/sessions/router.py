from fastapi import APIRouter, HTTPException
from database import get_db_connection
from models import *

router = APIRouter()


@router.get("/api/sessions/upcoming", response_model=List[SessionResponse], tags=["Sessions"])
def get_upcoming_sessions():
    """
    Fetches future sessions. 
    Counts only 'booked' status bookings to show current accurate capacity.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT s.session_id, s.session_name, s.schedule_date, s.start_time, s.end_time, s.max_capacity,
               t.first_name AS trainer_first_name, t.last_name AS trainer_last_name,
               COUNT(sb.booking_id) AS current_bookings
        FROM sessions s
        JOIN trainers t ON s.trainer_id = t.trainer_id
        LEFT JOIN session_bookings sb ON s.session_id = sb.session_id AND sb.status = 'booked'
        WHERE s.schedule_date >= CURRENT_DATE
        GROUP BY s.session_id, t.trainer_id
        ORDER BY s.schedule_date ASC, s.start_time ASC;
    """
    cursor.execute(query)
    sessions = cursor.fetchall()
    cursor.close()
    conn.close()
    return sessions


@router.get("/api/sessions/with-spots", response_model=List[SessionWithSpots], tags=["Sessions"])
def get_sessions_with_spots():
    """
    Calculates spots remaining dynamically: max_capacity - current booked count.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT s.session_id, s.session_name,
               t.first_name || ' ' || t.last_name AS trainer,
               s.schedule_date, s.start_time, s.end_time,
               s.max_capacity,
               s.max_capacity - COUNT(sb.booking_id) AS spots_remaining
        FROM sessions s
        JOIN trainers t ON s.trainer_id = t.trainer_id
        LEFT JOIN session_bookings sb ON s.session_id = sb.session_id AND sb.status = 'booked'
        GROUP BY s.session_id, s.session_name, t.first_name, t.last_name, s.schedule_date, s.start_time, s.end_time, s.max_capacity
        ORDER BY s.schedule_date, s.start_time;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/sessions/fill-rate", response_model=List[SessionFillRate], tags=["Sessions"])
def get_session_fill_rate():
    """
    Calculates percentage full for each session.
    Uses 100.0 to force float division in SQL, avoiding integer rounding to 0.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT s.session_name, s.schedule_date,
               s.max_capacity,
               COUNT(sb.booking_id) AS booked,
               ROUND(COUNT(sb.booking_id) * 100.0 / s.max_capacity, 1) AS fill_pct
        FROM sessions s
        LEFT JOIN session_bookings sb ON s.session_id = sb.session_id AND sb.status = 'booked'
        GROUP BY s.session_id, s.session_name, s.schedule_date, s.max_capacity
        ORDER BY fill_pct DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/sessions/{session_id}/bookings", response_model=List[SessionBookingsResponse], tags=["Sessions"])
def get_session_bookings(session_id: int):
    """Fetches all members booked into a specific session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT sb.booking_id, m.first_name || ' ' || m.last_name AS member,
               sb.booking_date, sb.status
        FROM session_bookings sb
        JOIN members m ON sb.member_id = m.member_id
        WHERE sb.session_id = %s;
    """
    cursor.execute(query, (session_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.post("/api/sessions/book", tags=["Sessions"])
def book_session(booking_data: BookingRequest):
    """
    Books a session for a member.
    Uses try/except to catch unique constraint violations (double booking).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO session_bookings (session_id, member_id, status) 
            VALUES (%s, %s, 'booked');
        """, (booking_data.session_id, booking_data.member_id))
        conn.commit()
        return {"message": "Session booked successfully!"}
    except Exception as e:
        conn.rollback()
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Member already booked this session")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.patch("/api/sessions/cancel-booking", tags=["Sessions"])
def cancel_booking(booking_data: BookingRequest):
    """Cancels a specific booking for a member."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE session_bookings SET status = 'cancelled' 
        WHERE session_id = %s AND member_id = %s;
    """, (booking_data.session_id, booking_data.member_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Booking cancelled."}


@router.get("/api/members/{member_id}/sessions/upcoming", response_model=List[MemberBookingHistory], tags=["Sessions"])
def get_member_upcoming_sessions(member_id: int):
    """Fetches a member's future booked sessions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT s.session_name, s.schedule_date, s.start_time, s.end_time, 
               t.first_name AS trainer_name, sb.status
        FROM session_bookings sb
        JOIN sessions s ON sb.session_id = s.session_id
        JOIN trainers t ON s.trainer_id = t.trainer_id
        WHERE sb.member_id = %s AND s.schedule_date >= CURRENT_DATE
        ORDER BY s.schedule_date ASC;
    """
    cursor.execute(query, (member_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/members/{member_id}/sessions/history", response_model=List[MemberBookingHistory], tags=["Sessions"])
def get_member_session_history(member_id: int):
    """Fetches ALL past and future sessions a member has ever booked."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT s.session_name, s.schedule_date, s.start_time,
               t.first_name || ' ' || t.last_name AS trainer, sb.status
        FROM session_bookings sb
        JOIN sessions s ON sb.session_id = s.session_id
        JOIN trainers t ON s.trainer_id = t.trainer_id
        WHERE sb.member_id = %s
        ORDER BY s.schedule_date DESC;
    """
    cursor.execute(query, (member_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data
