from fastapi import APIRouter, HTTPException, status
from database import get_db_connection
from models import *

router = APIRouter()


@router.get("/api/dashboard/stats", response_model=DashboardStats, tags=["Dashboard"])
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


@router.post("/api/transactions/register-member", status_code=status.HTTP_201_CREATED, tags=["Transactions"])
def register_member_transaction(member_data: MemberCreateRequest):
    """
    TRANSACTION: Atomically creates a User AND a Member.
    RETURNING user_id captures the auto-incremented ID for the second insert.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password_hash, role) VALUES (%s, %s, 'member') RETURNING user_id;", (member_data.email, member_data.password))
        new_user_id = cursor.fetchone()["user_id"]
        cursor.execute("INSERT INTO members (user_id, first_name, last_name, phone, plan_id) VALUES (%s, %s, %s, %s, %s);", (new_user_id, member_data.first_name, member_data.last_name, member_data.phone, member_data.plan_id))
        conn.commit()
        return {"message": "Member registered via transaction!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/api/transactions/register-trainer", status_code=status.HTTP_201_CREATED, tags=["Transactions"])
def register_trainer_transaction(trainer_data: TrainerCreateRequest):
    """TRANSACTION: Atomically creates a User AND a Trainer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password_hash, role) VALUES (%s, %s, 'trainer') RETURNING user_id;", (trainer_data.email, trainer_data.password))
        new_user_id = cursor.fetchone()["user_id"]
        cursor.execute("INSERT INTO trainers (user_id, first_name, last_name, specialization, phone) VALUES (%s, %s, %s, %s, %s);", (new_user_id, trainer_data.first_name, trainer_data.last_name, trainer_data.specialization, trainer_data.phone))
        conn.commit()
        return {"message": "Trainer registered via transaction!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/api/transactions/check-in-session", tags=["Transactions"])
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


@router.post("/api/transactions/process-overdue", tags=["Transactions"])
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


@router.post("/api/transactions/assign-plan", tags=["Transactions"])
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


@router.patch("/api/transactions/deactivate-member/{member_id}", tags=["Transactions"])
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


@router.patch("/api/transactions/transfer-session", tags=["Transactions"])
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


@router.delete("/api/transactions/delete-member/{member_id}", tags=["Transactions"])
def delete_member_permanently(member_id: int):
    """TRANSACTION: Cancels bookings, then deletes User (which cascades to Member)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE session_bookings SET status = 'canceled' WHERE member_id = %s;", (member_id,))
        cursor.execute("DELETE FROM users WHERE user_id = (SELECT user_id FROM members WHERE member_id = %s);", (member_id,))
        conn.commit()
        return {"message": f"Member {member_id} and user account permanently deleted."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/api/analytics/member-activity-union", response_model=List[MemberActivity], tags=["Advanced Analytics"])
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


@router.get("/api/analytics/member-dashboard-view", response_model=List[MemberDashboardView], tags=["Advanced Analytics"])
def get_member_dashboard_view():
    """Fetches data directly from the pre-built vw_member_dashboard View."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vw_member_dashboard ORDER BY total_paid DESC;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/analytics/session-capacity-view", response_model=List[SessionCapacityView], tags=["Advanced Analytics"])
def get_session_capacity_view():
    """Fetches data directly from the pre-built vw_session_capacity View."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vw_session_capacity ORDER BY schedule_date ASC;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/analytics/active-members-intersect", response_model=List[SimpleMemberId], tags=["Advanced Analytics"])
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


@router.get("/api/analytics/absent-active-members", response_model=List[SimpleMemberId], tags=["Advanced Analytics"])
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


@router.get("/api/analytics/incomplete-bookings", response_model=List[SimpleMemberId], tags=["Advanced Analytics"])
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


@router.get("/api/plans/pricing-breakdown", response_model=List[PlanPricingBreakdown], tags=["Advanced Analytics"])
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


@router.get("/api/payments/above-average", response_model=List[AboveAveragePayment], tags=["Advanced Analytics"])
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


@router.get("/api/analytics/attendance-ranking", response_model=List[AttendanceRank], tags=["Advanced Analytics"])
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


@router.get("/api/analytics/revenue-running-total", response_model=List[RunningTotalRevenue], tags=["Advanced Analytics"])
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
