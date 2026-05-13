from fastapi import APIRouter
from database import get_db_connection
from models import *

router = APIRouter()


@router.get("/api/trainers", response_model=List[TrainerResponse], tags=["Trainers"])
def get_all_trainers():
    """
    Fetches all trainers.
    INNER JOIN ensures we only get users who are trainers.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT t.trainer_id, t.first_name || ' ' || t.last_name AS full_name,
               t.specialization, t.hire_date, t.phone, u.email
        FROM trainers t
        JOIN users u ON t.user_id = u.user_id
        ORDER BY t.hire_date;
    """
    cursor.execute(query)
    trainers = cursor.fetchall()
    cursor.close()
    conn.close()
    return trainers


@router.get("/{trainer_id}/schedule", response_model=List[TrainerScheduleResponse], tags=["Trainers"])
def get_trainer_schedule(trainer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    # This SQL matches our new model perfectly!
    query = """
        SELECT session_id, session_name, schedule_date, start_time, end_time, max_capacity
        FROM sessions
        WHERE trainer_id = %s
        ORDER BY schedule_date, start_time;
    """
    cursor.execute(query, (trainer_id,))
    sessions = cursor.fetchall()
    cursor.close()
    conn.close()
    return sessions


@router.get("/api/trainers/session-count", response_model=List[TrainerSessionCount], tags=["Trainers"])
def count_sessions_per_trainer():
    """
    Groups data by trainer to show how many sessions they conduct.
    LEFT JOIN ensures trainers with 0 sessions still show up.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT t.first_name || ' ' || t.last_name AS trainer,
               COUNT(s.session_id) AS total_sessions
        FROM trainers t
        LEFT JOIN sessions s ON t.trainer_id = s.trainer_id
        GROUP BY t.trainer_id, t.first_name, t.last_name
        ORDER BY total_sessions DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/trainers/workload", response_model=List[TrainerWorkload], tags=["Trainers"])
def get_trainer_workload():
    """
    Complex analytics: Combines trainers, their sessions, and the bookings for those sessions.
    COUNT(DISTINCT) ensures sessions aren't counted multiple times if they have multiple bookings.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            t.first_name AS trainer_name,
            t.specialization,
            COUNT(DISTINCT s.session_id) AS total_sessions,
            COUNT(sb.booking_id) AS total_bookings
        FROM trainers t
        LEFT JOIN sessions s ON t.trainer_id = s.trainer_id
        LEFT JOIN session_bookings sb ON s.session_id = sb.session_id AND sb.status = 'booked'
        GROUP BY t.trainer_id, t.first_name, t.specialization
        ORDER BY total_bookings DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data
