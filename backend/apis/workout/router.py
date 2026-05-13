from fastapi import APIRouter, HTTPException, status
from database import get_db_connection
from models import *

router = APIRouter()


@router.post("/api/workouts", status_code=status.HTTP_201_CREATED, tags=["Workouts"])
def add_workout(workout_data: WorkoutCreateRequest):
    """Logs a new workout assigned by a trainer to a member."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO workouts (member_id, trainer_id, routine_description, performance_notes) 
            VALUES (%s, %s, %s, %s);
        """, (workout_data.member_id, workout_data.trainer_id, workout_data.routine_description, workout_data.performance_notes))
        conn.commit()
        return {"message": "Workout logged successfully!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/api/workouts", response_model=List[AllWorkoutsResponse], tags=["Workouts"])
def get_all_workouts():
    """Admin view: Fetches all workouts across the gym with member and trainer names."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT w.workout_id,
               m.first_name || ' ' || m.last_name AS member,
               t.first_name || ' ' || t.last_name AS trainer,
               w.workout_date, w.routine_description, w.performance_notes
        FROM workouts w
        JOIN members m ON w.member_id = m.member_id
        JOIN trainers t ON w.trainer_id = t.trainer_id
        ORDER BY w.workout_date DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/members/{member_id}/workouts", response_model=List[WorkoutResponse], tags=["Workouts"])
def get_member_workouts(member_id: int):
    """Member view: Fetches their last 10 workouts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT w.workout_date, w.routine_description, w.performance_notes,
               t.first_name AS trainer_first_name
        FROM workouts w
        LEFT JOIN trainers t ON w.trainer_id = t.trainer_id
        WHERE w.member_id = %s
        ORDER BY w.workout_date DESC
        LIMIT 10;
    """
    cursor.execute(query, (member_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/trainers/{trainer_id}/workouts", response_model=List[WorkoutResponse], tags=["Workouts"])
def get_trainer_assigned_workouts(trainer_id: int):
    """Trainer view: Fetches all workouts this specific trainer has assigned."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT w.workout_date, w.routine_description, w.performance_notes
        FROM workouts w
        JOIN members m ON w.member_id = m.member_id
        WHERE w.trainer_id = %s
        ORDER BY w.workout_date DESC;
    """
    cursor.execute(query, (trainer_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data
