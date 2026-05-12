from fastapi import FastAPI, HTTPException, status
from database import get_db_connection
from models import *

# Initialize the FastAPI app with a title and version shown in Swagger docs
app = FastAPI(title="Gym Management System API", version="2.0")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows React dev server to connect
    allow_credentials=True,
    allow_methods=["*"], # Allows GET, POST, etc.
    allow_headers=["*"], # Allows all headers
)

# ==========================================
# AUTHENTICATION
# ==========================================
@app.post("/api/auth/login", response_model=LoginResponse, tags=["Authentication"])
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
    if not user or user['password_hash'] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    # 2. NEW: CHECK IF USER IS AN ADMIN! If not, block them.
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Access Denied. Admin portal only.")
        
    # Remove password hash before sending data to the frontend
    del user['password_hash']
    return user


# ==========================================
# MEMBERS
# ==========================================
@app.get("/api/members", response_model=List[MemberResponse], tags=["Members"])
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

@app.patch("/api/members/{member_id}/status", tags=["Members"])
def update_member_status(member_id: int, status_data: UpdateMemberStatus):
    """Updates a specific member's status (e.g., freezing their account)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Simple update query filtering by member_id
    cursor.execute("UPDATE members SET status = %s WHERE member_id = %s;", (status_data.status, member_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"Member {member_id} status updated to {status_data.status}"}

@app.get("/api/members/{member_id}/dashboard", response_model=MemberDashboard, tags=["Members"])
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
    if not dash: raise HTTPException(status_code=404, detail="Member not found")
    return dash


# ==========================================
# TRAINERS
# ==========================================
@app.get("/api/trainers", response_model=List[TrainerResponse], tags=["Trainers"])
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

@app.get("/api/trainers/{trainer_id}/schedule", response_model=List[SessionResponse], tags=["Trainers"])
def get_trainer_schedule(trainer_id: int):
    """Fetches all sessions assigned to a specific trainer."""
    conn = get_db_connection()
    cursor = conn.cursor()
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

@app.get("/api/trainers/session-count", response_model=List[TrainerSessionCount], tags=["Trainers"])
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

@app.get("/api/trainers/workload", response_model=List[TrainerWorkload], tags=["Trainers"])
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


# ==========================================
# MEMBERSHIP PLANS
# ==========================================
@app.get("/api/plans", response_model=List[PlanResponse], tags=["Plans"])
def get_all_plans():
    """Fetches all available membership plans ordered by price."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT plan_id, plan_name, duration_months, price, description FROM membership_plans ORDER BY price ASC;")
    plans = cursor.fetchall()
    cursor.close()
    conn.close()
    return plans

@app.post("/api/plans", status_code=status.HTTP_201_CREATED, tags=["Plans"])
def create_plan(plan_data: PlanCreateRequest):
    """Inserts a new custom membership plan into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO membership_plans (plan_name, duration_months, price, description) VALUES (%s, %s, %s, %s);",
        (plan_data.plan_name, plan_data.duration_months, plan_data.price, plan_data.description)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Plan created successfully!"}


# ==========================================
# SESSIONS & BOOKINGS
# ==========================================
@app.get("/api/sessions/upcoming", response_model=List[SessionResponse], tags=["Sessions"])
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

@app.get("/api/sessions/with-spots", response_model=List[SessionWithSpots], tags=["Sessions"])
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

@app.get("/api/sessions/fill-rate", response_model=List[SessionFillRate], tags=["Sessions"])
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

@app.get("/api/sessions/{session_id}/bookings", response_model=List[SessionBookingsResponse], tags=["Sessions"])
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

@app.post("/api/sessions/book", tags=["Sessions"])
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
        conn.rollback() # Undo any partial DB changes on error
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Member already booked this session")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.patch("/api/sessions/cancel-booking", tags=["Sessions"])
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

@app.get("/api/members/{member_id}/sessions/upcoming", response_model=List[MemberBookingHistory], tags=["Sessions"])
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

@app.get("/api/members/{member_id}/sessions/history", response_model=List[MemberBookingHistory], tags=["Sessions"])
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


# ==========================================
# WORKOUTS
# ==========================================
@app.post("/api/workouts", status_code=status.HTTP_201_CREATED, tags=["Workouts"])
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

@app.get("/api/workouts", response_model=List[AllWorkoutsResponse], tags=["Workouts"])
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

@app.get("/api/members/{member_id}/workouts", response_model=List[WorkoutResponse], tags=["Workouts"])
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

@app.get("/api/trainers/{trainer_id}/workouts", response_model=List[WorkoutResponse], tags=["Workouts"])
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


# ==========================================
# ATTENDANCE
# ==========================================
@app.post("/api/attendance", tags=["Attendance"])
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

@app.get("/api/attendance", response_model=List[AttendanceLogResponse], tags=["Attendance"])
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

@app.get("/api/attendance/most-active", response_model=List[MemberVisitCount], tags=["Attendance"])
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

@app.get("/api/attendance/lazy-members", response_model=List[LazyMemberResponse], tags=["Attendance"])
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

@app.get("/api/members/{member_id}/attendance", response_model=List[dict], tags=["Attendance"])
def get_member_attendance(member_id: int):
    """Member view: Fetches their personal check-in history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT check_in FROM attendance WHERE member_id = %s ORDER BY check_in DESC;", (member_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/attendance/today-count", tags=["Attendance"])
def get_todays_attendance_count():
    """Dashboard stat: How many people checked in today."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS check_ins_today FROM attendance WHERE DATE(check_in) = CURRENT_DATE;")
    count = cursor.fetchone()
    cursor.close()
    conn.close()
    return count


# ==========================================
# PAYMENTS
# ==========================================
@app.post("/api/payments", tags=["Payments"])
def record_payment(payment_data: PaymentCreateRequest):
    """Records a new payment manually (as per project assumptions)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO payments (member_id, amount, payment_method, status) 
            VALUES (%s, %s, %s, %s);
        """, (payment_data.member_id, payment_data.amount, payment_data.payment_method, payment_data.status))
        conn.commit()
        return {"message": "Payment recorded!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/payments", response_model=List[AllPaymentsResponse], tags=["Payments"])
def get_all_payments():
    """Admin view: All payments with member names."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT p.payment_id, m.first_name || ' ' || m.last_name AS member,
               p.amount, p.payment_date, p.payment_method, p.status
        FROM payments p
        JOIN members m ON p.member_id = m.member_id
        ORDER BY p.payment_date DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/members/{member_id}/payments", response_model=List[PaymentResponse], tags=["Payments"])
def get_member_payments(member_id: int):
    """Member view: Their payment history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT amount, payment_date, payment_method, status FROM payments WHERE member_id = %s ORDER BY payment_date DESC;", (member_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/payments/overdue", response_model=List[AllPaymentsResponse], tags=["Payments"])
def get_overdue_payments():
    """Admin view: Finds payments that are pending or overdue."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT p.payment_id, m.first_name || ' ' || m.last_name AS member,
               p.amount, p.payment_date, p.payment_method, p.status
        FROM payments p
        JOIN members m ON p.member_id = m.member_id
        WHERE p.status IN ('pending', 'overdue')
        ORDER BY p.payment_date ASC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.patch("/api/payments/{payment_id}/mark-paid", tags=["Payments"])
def mark_payment_paid(payment_id: int):
    """Updates a specific payment status to paid (retrieved ID from overdue list)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE payments SET status = 'paid' WHERE payment_id = %s;", (payment_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"Payment {payment_id} marked as paid."}

@app.get("/api/payments/revenue-by-method", response_model=List[RevenueByMethod], tags=["Payments"])
def get_revenue_by_method():
    """Groups revenue by payment method (Cash, Bank Transfer)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT payment_method,
               COUNT(*) AS total_transactions,
               SUM(amount) AS total_collected
        FROM payments
        WHERE status = 'paid'
        GROUP BY payment_method;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/payments/revenue-by-plan", response_model=List[RevenueByPlan], tags=["Payments"])
def get_revenue_by_plan():
    """Calculates total revenue generated by each membership plan."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT mp.plan_name,
               COUNT(m.member_id) AS total_members,
               SUM(p.amount) AS total_revenue
        FROM membership_plans mp
        LEFT JOIN members m ON mp.plan_id = m.plan_id
        LEFT JOIN payments p ON m.member_id = p.member_id AND p.status = 'paid'
        GROUP BY mp.plan_name, mp.plan_id
        ORDER BY total_revenue DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/payments/detailed-revenue-by-plan", response_model=List[DetailedRevenueByPlan], tags=["Payments"])
def get_detailed_revenue_by_plan():
    """Advanced analytics: Count, Sum, and Average payments per plan."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT mp.plan_name,
               COUNT(p.payment_id) AS total_payments,
               SUM(p.amount) AS total_revenue,
               AVG(p.amount) AS avg_payment
        FROM payments p
        JOIN members m ON p.member_id = m.member_id
        JOIN membership_plans mp ON m.plan_id = mp.plan_id
        WHERE p.status = 'paid'
        GROUP BY mp.plan_name
        ORDER BY total_revenue DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/payments/monthly-revenue", response_model=List[MonthlyRevenue], tags=["Payments"])
def get_monthly_revenue():
    """Formats dates to YYYY-MM and groups revenue for charts over last 6 months."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT TO_CHAR(payment_date, 'YYYY-MM') AS month, SUM(amount) AS total_revenue
        FROM payments
        WHERE status = 'paid' AND payment_date >= CURRENT_DATE - INTERVAL '6 months'
        GROUP BY TO_CHAR(payment_date, 'YYYY-MM')
        ORDER BY month ASC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/payments/top-payers", response_model=List[TopPayingMember], tags=["Payments"])
def get_top_paying_members():
    """Ranks members by total amount paid."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.first_name || ' ' || m.last_name AS member,
               SUM(p.amount) AS total_paid,
               COUNT(p.payment_id) AS num_payments
        FROM payments p
        JOIN members m ON p.member_id = m.member_id
        WHERE p.status = 'paid'
        GROUP BY m.member_id, m.first_name, m.last_name
        ORDER BY total_paid DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


# ==========================================
# EQUIPMENT
# ==========================================
@app.get("/api/equipment", response_model=List[EquipmentResponse], tags=["Equipment"])
def get_all_equipment():
    """Fetches all equipment inventory."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment ORDER BY category, name;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/equipment/maintenance-alerts", response_model=List[MaintenanceAlert], tags=["Equipment"])
def get_maintenance_alerts():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT e.equipment_id, name, category, condition_status,
               next_maintenance_date,
               next_maintenance_date - CURRENT_DATE AS days_until_maintenance
        FROM equipment e
        WHERE next_maintenance_date <= CURRENT_DATE + 30
           OR condition_status ILIKE 'broken'      /* <-- Changed to ILIKE */
           OR condition_status ILIKE 'needs repair' /* <-- Changed to ILIKE */
        ORDER BY next_maintenance_date;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.patch("/api/equipment/{equipment_id}/condition", tags=["Equipment"])
def update_equipment_condition(equipment_id: int, cond_data: UpdateEquipmentStatus):
    """Updates equipment condition (e.g., marking it as broken)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE equipment SET condition_status = %s, next_maintenance_date = CURRENT_DATE 
        WHERE equipment_id = %s;
    """, (cond_data.condition_status, equipment_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Equipment condition updated."}

@app.patch("/api/equipment/{equipment_id}/repair-complete", tags=["Equipment"])
def complete_equipment_repair(equipment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE equipment SET condition_status = 'good', next_maintenance_date = CURRENT_DATE + INTERVAL '6 months' 
        WHERE equipment_id = %s;
    """, (equipment_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Equipment repaired and next maintenance scheduled."}


# ==========================================
# DASHBOARD
# ==========================================
@app.get("/api/dashboard/stats", response_model=DashboardStats, tags=["Dashboard"])
def get_dashboard_stats():
    """
    Super-query combining multiple subqueries to get all dashboard stats in one API call.
    COALESCE prevents returning NULL if sums are 0.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT
            (SELECT COUNT(*) FROM members WHERE status = 'active') AS active_members,
            (SELECT COUNT(*) FROM trainers) AS total_trainers,
            (SELECT COUNT(*) FROM sessions WHERE schedule_date >= CURRENT_DATE) AS upcoming_sessions,
            (SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'paid') AS total_revenue,
            (SELECT COUNT(*) FROM payments WHERE status IN ('pending','overdue')) AS pending_payments,
            (SELECT COUNT(*) FROM equipment WHERE condition_status != 'Good') AS equipment_issues,
            (SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'paid' AND DATE(payment_date) = CURRENT_DATE) AS revenue_today,
            (SELECT COUNT(*) FROM sessions WHERE schedule_date = CURRENT_DATE) AS sessions_today;
    """
    cursor.execute(query)
    stats = cursor.fetchone()
    cursor.close()
    conn.close()
    return stats


# ==========================================
# TRANSACTIONS
# ==========================================
@app.post("/api/transactions/register-member", status_code=status.HTTP_201_CREATED, tags=["Transactions"])
def register_member_transaction(member_data: MemberCreateRequest):
    """
    TRANSACTION: Atomically creates a User AND a Member.
    RETURNING user_id captures the auto-incremented ID for the second insert.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password_hash, role) VALUES (%s, %s, 'member') RETURNING user_id;", (member_data.email, member_data.password))
        new_user_id = cursor.fetchone()['user_id']
        cursor.execute("INSERT INTO members (user_id, first_name, last_name, phone, plan_id) VALUES (%s, %s, %s, %s, %s);", (new_user_id, member_data.first_name, member_data.last_name, member_data.phone, member_data.plan_id))
        conn.commit() # Commits both inserts together
        return {"message": "Member registered via transaction!"}
    except Exception as e:
        conn.rollback() # Undoes the first insert if the second one fails
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/transactions/register-trainer", status_code=status.HTTP_201_CREATED, tags=["Transactions"])
def register_trainer_transaction(trainer_data: TrainerCreateRequest):
    """TRANSACTION: Atomically creates a User AND a Trainer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password_hash, role) VALUES (%s, %s, 'trainer') RETURNING user_id;", (trainer_data.email, trainer_data.password))
        new_user_id = cursor.fetchone()['user_id']
        cursor.execute("INSERT INTO trainers (user_id, first_name, last_name, specialization, phone) VALUES (%s, %s, %s, %s, %s);", (new_user_id, trainer_data.first_name, trainer_data.last_name, trainer_data.specialization, trainer_data.phone))
        conn.commit()
        return {"message": "Trainer registered via transaction!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/transactions/check-in-session", tags=["Transactions"])
def check_in_for_session(booking_data: BookingRequest):
    """TRANSACTION: Marks booking as completed AND logs attendance simultaneously."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE session_bookings SET status = 'completed' WHERE member_id = %s AND session_id = %s;", (booking_data.member_id, booking_data.session_id))
        cursor.execute("INSERT INTO attendance (member_id) VALUES (%s);", (booking_data.member_id,))
        conn.commit()
        return {"message": "Checked in and attendance recorded!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/transactions/process-overdue", tags=["Transactions"])
def process_overdue_payments():
    """TRANSACTION: Marks old payments as overdue AND freezes those member accounts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE payments SET status = 'overdue' WHERE status = 'pending' AND payment_date < CURRENT_DATE - INTERVAL '30 days';")
        cursor.execute("UPDATE members SET status = 'frozen' WHERE member_id IN (SELECT DISTINCT member_id FROM payments WHERE status = 'overdue') AND status = 'active';")
        conn.commit()
        return {"message": "Overdue payments processed and accounts frozen!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/transactions/assign-plan", tags=["Transactions"])
def assign_new_plan(assign_data: AssignPlanRequest):
    """TRANSACTION: Updates a member's plan AND records the payment for it."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE members SET plan_id = %s WHERE member_id = %s;", (assign_data.plan_id, assign_data.member_id))
        cursor.execute("INSERT INTO payments (member_id, amount, payment_date, payment_method, status) VALUES (%s, %s, CURRENT_DATE, %s, 'paid');", (assign_data.member_id, assign_data.amount, assign_data.payment_method))
        conn.commit()
        return {"message": "New plan assigned and payment recorded!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.patch("/api/transactions/deactivate-member/{member_id}", tags=["Transactions"])
def deactivate_member_transaction(member_id: int):
    """TRANSACTION: Sets member to inactive AND cancels all their active bookings."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE members SET status = 'inactive' WHERE member_id = %s;", (member_id,))
        cursor.execute("UPDATE session_bookings SET status = 'canceled' WHERE member_id = %s AND status = 'booked';", (member_id,))
        conn.commit()
        return {"message": f"Member {member_id} deactivated and bookings canceled."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.patch("/api/transactions/transfer-session", tags=["Transactions"])
def transfer_session(transfer_data: TransferSessionRequest):
    """TRANSACTION (single query, but structured for future extension): Moves a session to a new trainer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE sessions SET trainer_id = %s WHERE session_id = %s;", (transfer_data.new_trainer_id, transfer_data.session_id))
        conn.commit()
        return {"message": "Session transferred successfully!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/transactions/delete-member/{member_id}", tags=["Transactions"])
def delete_member_permanently(member_id: int):
    """TRANSACTION: Cancels bookings, then deletes User (which cascades to Member)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE session_bookings SET status = 'canceled' WHERE member_id = %s;", (member_id,))
        # Deleting from Users cascades to Members because of ON DELETE CASCADE in the DB schema
        cursor.execute("DELETE FROM users WHERE user_id = (SELECT user_id FROM members WHERE member_id = %s);", (member_id,))
        conn.commit()
        return {"message": f"Member {member_id} and user account permanently deleted."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ==========================================
# ZAID'S SET FUNCTIONS & ADVANCED ANALYTICS
# ==========================================
@app.get("/api/analytics/member-activity-union", response_model=List[MemberActivity], tags=["Advanced Analytics"])
def get_member_activity_union():
    """
    SET OPERATION (UNION): Combines member IDs from attendance and bookings into one list.
    Useful for knowing every member who has interacted with the gym.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT member_id, 'attendance' AS activity FROM attendance
        UNION
        SELECT member_id, 'booking' AS activity FROM session_bookings;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/analytics/active-members-intersect", response_model=List[SimpleMemberId], tags=["Advanced Analytics"])
def get_active_members_intersect():
    """
    SET OPERATION (INTERSECT): Finds members who BOTH checked in AND logged a workout.
    Shows highly engaged members.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT member_id FROM attendance
        INTERSECT
        SELECT member_id FROM workouts;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/analytics/absent-active-members", response_model=List[SimpleMemberId], tags=["Advanced Analytics"])
def get_absent_active_members():
    """
    SET OPERATION (EXCEPT/MINUS): Finds active members EXCEPT those who checked in.
    Identifies paying members wasting their money.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT member_id FROM members WHERE status = 'active'
        EXCEPT
        SELECT DISTINCT member_id FROM attendance;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/analytics/incomplete-bookings", response_model=List[SimpleMemberId], tags=["Advanced Analytics"])
def get_incomplete_bookings():
    """SET OPERATION (EXCEPT): Members who booked but never completed a session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT member_id FROM session_bookings WHERE status = 'booked'
        EXCEPT
        SELECT member_id FROM session_bookings WHERE status = 'completed';
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/plans/pricing-breakdown", response_model=List[PlanPricingBreakdown], tags=["Advanced Analytics"])
def get_plan_pricing_breakdown():
    """
    ARITHMETIC: Uses SQL math functions to calculate monthly rates and 10% discounts dynamically.
    ROUND ensures clean 2-decimal currency formats.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT plan_name,
               price AS total_price,
               ROUND(price / duration_months, 2) AS monthly_rate,
               ROUND(price * 0.10, 2) AS ten_pct_discount,
               ROUND(price - (price * 0.10), 2) AS discounted_price
        FROM membership_plans;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/payments/above-average", response_model=List[AboveAveragePayment], tags=["Advanced Analytics"])
def get_above_average_payments():
    """
    SUBQUERY: Finds payments greater than the average payment amount.
    The inner query calculates the average, the outer query filters by it.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.first_name || ' ' || m.last_name AS member, p.amount
        FROM payments p
        JOIN members m ON p.member_id = m.member_id
        WHERE p.amount > (SELECT AVG(amount) FROM payments WHERE status = 'paid')
        ORDER BY p.amount DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/analytics/attendance-ranking", response_model=List[AttendanceRank], tags=["Advanced Analytics"])
def get_attendance_ranking():
    """
    WINDOW FUNCTION (RANK): Assigns a rank to members based on visits.
    RANK() handles ties (e.g., two people with 10 visits both get Rank 1, next gets Rank 3).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.first_name || ' ' || m.last_name AS member,
               COUNT(a.attendance_id) AS visits,
               RANK() OVER (ORDER BY COUNT(a.attendance_id) DESC) AS rank
        FROM attendance a
        JOIN members m ON a.member_id = m.member_id
        GROUP BY m.member_id, m.first_name, m.last_name;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/analytics/revenue-running-total", response_model=List[RunningTotalRevenue], tags=["Advanced Analytics"])
def get_revenue_running_total():
    """
    WINDOW FUNCTION (SUM OVER): Calculates a cumulative sum of revenue over time.
    Shows the total revenue growth day by day, rather than just daily chunks.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT payment_date, amount,
               SUM(amount) OVER (ORDER BY payment_date) AS running_total
        FROM payments
        WHERE status = 'paid'
        ORDER BY payment_date;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/analytics/member-dashboard-view", response_model=List[MemberDashboardView], tags=["Advanced Analytics"])
def get_member_dashboard_view():
    """Fetches data directly from the pre-built vw_member_dashboard View."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Notice how simple the query is now! The database does the heavy lifting.
    cursor.execute("SELECT * FROM vw_member_dashboard ORDER BY total_paid DESC;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/analytics/session-capacity-view", response_model=List[SessionCapacityView], tags=["Advanced Analytics"])
def get_session_capacity_view():
    """Fetches data directly from the pre-built vw_session_capacity View."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vw_session_capacity ORDER BY schedule_date ASC;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data
