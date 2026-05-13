from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    TIMESTAMP,
    Date,
    Time,
    Text,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    text
)
from sqlalchemy.orm import relationship

from database import Base


class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    members = relationship("Members", back_populates="user")
    trainers = relationship("Trainers", back_populates="user")

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'trainer', 'member')",
            name="check_user_role"
        ),
    )


class MembershipPlans(Base):
    __tablename__ = "membership_plans"

    plan_id = Column(Integer, primary_key=True, nullable=False)
    plan_name = Column(String(50), nullable=False)
    duration_months = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text)

    members = relationship("Members", back_populates="membership_plan")


class Members(Base):
    __tablename__ = "members"

    member_id = Column(Integer, primary_key=True, nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(15))

    join_date = Column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE")
    )

    plan_id = Column(
        Integer,
        ForeignKey("membership_plans.plan_id", ondelete="SET NULL"),
        nullable=True
    )

    status = Column(
        String(20),
        nullable=False,
        server_default=text("'active'")
    )

    user = relationship("Users", back_populates="members")
    membership_plan = relationship("MembershipPlans", back_populates="members")

    payments = relationship("Payments", back_populates="member")
    bookings = relationship("SessionBookings", back_populates="member")
    attendance_records = relationship("Attendance", back_populates="member")
    workouts = relationship("Workouts", back_populates="member")

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'frozen')",
            name="check_member_status"
        ),
    )


class Trainers(Base):
    __tablename__ = "trainers"

    trainer_id = Column(Integer, primary_key=True, nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    specialization = Column(String(100))

    hire_date = Column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE")
    )

    phone = Column(String(15))

    user = relationship("Users", back_populates="trainers")

    sessions = relationship("Sessions", back_populates="trainer")
    workouts = relationship("Workouts", back_populates="trainer")


class Payments(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, nullable=False)

    member_id = Column(
        Integer,
        ForeignKey("members.member_id", ondelete="CASCADE"),
        nullable=False
    )

    amount = Column(DECIMAL(10, 2), nullable=False)

    payment_date = Column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE")
    )

    payment_method = Column(
        String(50),
        nullable=False,
        server_default=text("'cash'")
    )

    status = Column(
        String(20),
        nullable=False,
        server_default=text("'paid'")
    )

    member = relationship("Members", back_populates="payments")

    __table_args__ = (
        CheckConstraint(
            "status IN ('paid', 'pending', 'overdue')",
            name="check_payment_status"
        ),
    )


class Sessions(Base):
    __tablename__ = "sessions"

    session_id = Column(Integer, primary_key=True, nullable=False)

    trainer_id = Column(
        Integer,
        ForeignKey("trainers.trainer_id", ondelete="CASCADE"),
        nullable=False
    )

    session_name = Column(String(100), nullable=False)

    schedule_date = Column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE")
    )

    start_time = Column(
        Time,
        nullable=False,
        server_default=text("CURRENT_TIME")
    )

    end_time = Column(
        Time,
        nullable=False,
        server_default=text("CURRENT_TIME")
    )

    max_capacity = Column(
        Integer,
        nullable=False,
        server_default=text("20")
    )

    trainer = relationship("Trainers", back_populates="sessions")
    bookings = relationship("SessionBookings", back_populates="session")


class SessionBookings(Base):
    __tablename__ = "session_bookings"

    booking_id = Column(Integer, primary_key=True, nullable=False)

    session_id = Column(
        Integer,
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False
    )

    member_id = Column(
        Integer,
        ForeignKey("members.member_id", ondelete="CASCADE"),
        nullable=False
    )

    booking_date = Column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE")
    )

    status = Column(
        String(20),
        nullable=False,
        server_default=text("'booked'")
    )

    session = relationship("Sessions", back_populates="bookings")
    member = relationship("Members", back_populates="bookings")

    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "member_id",
            name="unique_session_booking"
        ),
        CheckConstraint(
            "status IN ('booked', 'canceled', 'completed')",
            name="check_booking_status"
        ),
    )


class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True, nullable=False)

    member_id = Column(
        Integer,
        ForeignKey("members.member_id", ondelete="CASCADE"),
        nullable=False
    )

    check_in = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    member = relationship("Members", back_populates="attendance_records")


class Workouts(Base):
    __tablename__ = "workouts"

    workout_id = Column(Integer, primary_key=True, nullable=False)

    member_id = Column(
        Integer,
        ForeignKey("members.member_id", ondelete="CASCADE"),
        nullable=False
    )

    trainer_id = Column(
        Integer,
        ForeignKey("trainers.trainer_id", ondelete="SET NULL"),
        nullable=True
    )

    workout_date = Column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE")
    )

    routine_description = Column(Text, nullable=False)
    performance_notes = Column(Text)

    member = relationship("Members", back_populates="workouts")
    trainer = relationship("Trainers", back_populates="workouts")


class Equipment(Base):
    __tablename__ = "equipment"

    equipment_id = Column(Integer, primary_key=True, nullable=False)

    name = Column(String(100), nullable=False)
    category = Column(String(50))

    condition_status = Column(
        String(20),
        nullable=False,
        server_default=text("'good'")
    )

    purchase_date = Column(Date)
    next_maintenance_date = Column(Date)

    __table_args__ = (
        CheckConstraint(
            "condition_status IN ('good', 'needs repair', 'broken')",
            name="check_equipment_condition"
        ),
    )


def create_views(engine):
    view_statements = [
        """
        CREATE OR REPLACE VIEW vw_member_dashboard AS
        SELECT
            m.member_id,
            m.first_name || ' ' || m.last_name AS full_name,
            mp.plan_name,
            m.status,
            COALESCE(p.total_paid, 0) AS total_paid,
            COALESCE(a.total_visits, 0) AS total_visits
        FROM members m
        LEFT JOIN membership_plans mp ON m.plan_id = mp.plan_id
        LEFT JOIN (
            SELECT member_id, SUM(amount) AS total_paid
            FROM payments
            WHERE status = 'paid'
            GROUP BY member_id
        ) p ON p.member_id = m.member_id
        LEFT JOIN (
            SELECT member_id, COUNT(*) AS total_visits
            FROM attendance
            GROUP BY member_id
        ) a ON a.member_id = m.member_id;
        """,
        """
        CREATE OR REPLACE VIEW vw_session_capacity AS
        SELECT
            s.session_id,
            s.session_name,
            t.first_name || ' ' || t.last_name AS trainer,
            s.schedule_date,
            s.max_capacity,
            COALESCE(sb.current_bookings, 0) AS current_bookings,
            s.max_capacity - COALESCE(sb.current_bookings, 0) AS spots_remaining
        FROM sessions s
        JOIN trainers t ON s.trainer_id = t.trainer_id
        LEFT JOIN (
            SELECT session_id, COUNT(*) AS current_bookings
            FROM session_bookings
            WHERE status = 'booked'
            GROUP BY session_id
        ) sb ON sb.session_id = s.session_id;
        """,
    ]

    with engine.begin() as conn:
        for statement in view_statements:
            conn.execute(text(statement))
