from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime, time
# ==========================================================
# PYDANTIC MODELS (Data Validation & Serialization)
# These classes ensure the API receives and sends the exact 
# data structure expected. "Request" = Input, "Response" = Output
# ==========================================================

# --- AUTHENTICATION ---
class UserLogin(BaseModel):
    """Frontend sends email and password to log in"""
    email: str
    password: str

class LoginResponse(BaseModel):
    """Backend responds with user role and their specific DB IDs"""
    user_id: int
    role: str
    member_id: Optional[int] = None      # Only filled if user is a member
    member_first_name: Optional[str] = None
    trainer_id: Optional[int] = None     # Only filled if user is a trainer
    trainer_first_name: Optional[str] = None

# --- MEMBERS ---
class MemberCreateRequest(BaseModel):
    """Data required to register a new member"""
    email: str
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    plan_id: int

class MemberResponse(BaseModel):
    """Data returned when viewing member details"""
    member_id: int
    first_name: str
    last_name: str
    phone: Optional[str] = None
    join_date: date
    status: str
    plan_name: Optional[str] = None      # Joined from membership_plans table

class UpdateMemberStatus(BaseModel):
    """Payload to change a member's status (active/inactive/frozen)"""
    status: str 

class MemberDashboard(BaseModel):
    """Aggregated stats for a specific member's profile page"""
    full_name: str
    plan_name: Optional[str] = None
    duration_months: Optional[int] = None
    total_paid: Optional[float] = 0
    total_visits: Optional[int] = 0

# --- TRAINERS ---
class TrainerCreateRequest(BaseModel):
    """Data required to register a new trainer"""
    email: str
    password: str
    first_name: str
    last_name: str
    specialization: str
    phone: Optional[str] = None

class TrainerResponse(BaseModel):
    """Data returned when viewing trainer details"""
    trainer_id: int
    full_name: str                       # Concatenated from first + last name in SQL
    specialization: Optional[str] = None
    hire_date: date
    phone: Optional[str] = None
    email: str

class TrainerSessionCount(BaseModel):
    """Returns a trainer's name and how many sessions they teach"""
    trainer: str
    total_sessions: int

class TrainerWorkload(BaseModel):
    """Advanced trainer stats: sessions + total member bookings"""
    trainer_name: str
    specialization: Optional[str] = None
    total_sessions: int
    total_bookings: int

# --- PLANS ---
class PlanResponse(BaseModel):
    """Standard membership plan details"""
    plan_id: int
    plan_name: str
    duration_months: int
    price: float
    description: Optional[str] = None

class PlanCreateRequest(BaseModel):
    """Data required to create a custom/new plan"""
    plan_name: str
    duration_months: int
    price: float
    description: Optional[str] = None

class PlanPricingBreakdown(BaseModel):
    """Arithmetic breakdown of plan costs (Zaid's set functions)"""
    plan_name: str
    total_price: float
    monthly_rate: float
    ten_pct_discount: float
    discounted_price: float

# --- SESSIONS & BOOKINGS ---
class SessionCreateRequest(BaseModel):
    """Data required to create a new gym session"""
    trainer_id: int
    session_name: str
    schedule_date: date
    start_time: str
    end_time: str
    max_capacity: int = 20               # Default to 20 if not provided

class BookingRequest(BaseModel):
    """Payload to book or cancel a session for a member"""
    session_id: int
    member_id: int

class SessionResponse(BaseModel):
    session_id: int
    session_name: str
    schedule_date: date
    start_time: time          
    end_time: time            
    max_capacity: int
    trainer_first_name: Optional[str] = None
    trainer_last_name: Optional[str] = None
    current_bookings: int

class SessionWithSpots(BaseModel):
    session_id: int
    session_name: str
    trainer: Optional[str] = None
    schedule_date: date
    start_time: time         
    end_time: time           
    max_capacity: Optional[int] = 0
    spots_remaining: Optional[int] = 0

class MemberBookingHistory(BaseModel):
    """Member's view of their past or upcoming sessions"""
    session_name: str
    schedule_date: date
    start_time: str
    trainer: Optional[str] = None
    status: str

class SessionBookingsResponse(BaseModel):
    """Admin/Trainer view of who is booked in a specific session"""
    booking_id: int
    member: str
    booking_date: date
    status: str

class SessionFillRate(BaseModel):
    """Analytics: How full a session is (percentage)"""
    session_name: str
    schedule_date: date
    max_capacity: int
    booked: int
    fill_pct: float

# --- WORKOUTS ---
class WorkoutCreateRequest(BaseModel):
    """Data required to assign/log a workout"""
    member_id: int
    trainer_id: int
    routine_description: str
    performance_notes: Optional[str] = None

class WorkoutResponse(BaseModel):
    """Member's view of their workout history"""
    workout_date: date
    routine_description: str
    performance_notes: Optional[str] = None
    trainer_first_name: Optional[str] = None

class AllWorkoutsResponse(BaseModel):
    """Admin/Trainer view of all workouts logged"""
    workout_id: int
    member: str
    trainer: str
    workout_date: date
    routine_description: str
    performance_notes: Optional[str] = None

# --- ATTENDANCE ---
class CheckInRequest(BaseModel):
    """Payload to check a member into the gym"""
    member_id: int

class AttendanceLogResponse(BaseModel):
    """Full attendance record with member name"""
    attendance_id: int
    member: str
    check_in: datetime

class MemberVisitCount(BaseModel):
    """Analytics: Count of visits per member"""
    member: str
    total_visits: int

class LazyMemberResponse(BaseModel):
    """Members who have paid but never checked in"""
    member: str
    email: str

class AttendanceRank(BaseModel):
    """Ranking members by attendance using Window Functions"""
    member: str
    visits: int
    rank: int

# --- PAYMENTS ---
class PaymentCreateRequest(BaseModel):
    """Payload to record a new payment"""
    member_id: int
    amount: float
    payment_method: str
    status: str

class PaymentResponse(BaseModel):
    """Member's view of their payment history"""
    amount: float
    payment_date: date
    payment_method: str
    status: str

class AllPaymentsResponse(BaseModel):
    """Admin view of all payments with member names"""
    payment_id: int
    member: str
    amount: float
    payment_date: date
    payment_method: str
    status: str

class RevenueByMethod(BaseModel):
    """Analytics: Revenue grouped by payment method (Cash/Card etc)"""
    payment_method: str
    total_transactions: int
    total_collected: float

class RevenueByPlan(BaseModel):
    """Analytics: Revenue grouped by membership plan"""
    plan_name: str
    total_members: int
    total_revenue: float

class DetailedRevenueByPlan(BaseModel):
    """Advanced Analytics: Revenue, count, and average per plan"""
    plan_name: str
    total_payments: int
    total_revenue: float
    avg_payment: float

class MonthlyRevenue(BaseModel):
    """Analytics: Revenue tracked by month"""
    month: str
    total_revenue: float

class TopPayingMember(BaseModel):
    """Analytics: Members ranked by how much they have paid"""
    member: str
    total_paid: float
    num_payments: int

class AboveAveragePayment(BaseModel):
    """Subquery: Payments that exceed the average payment amount"""
    member: str
    amount: float

class RunningTotalRevenue(BaseModel):
    """Window Function: Running cumulative sum of revenue over time"""
    payment_date: date
    amount: float
    running_total: float

# --- EQUIPMENT ---
class EquipmentResponse(BaseModel):
    """Standard equipment details"""
    equipment_id: int
    name: str
    category: Optional[str] = None
    condition_status: str
    purchase_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None

class UpdateEquipmentStatus(BaseModel):
    """Payload to update if equipment is broken/good"""
    condition_status: str

class MaintenanceAlert(BaseModel):
    """Equipment needing repair or maintenance soon"""
    equipment_id: int
    name: str
    category: Optional[str] = None
    condition_status: str
    next_maintenance_date: Optional[date] = None
    days_until_maintenance: Optional[int] = None

# --- DASHBOARD ---
class DashboardStats(BaseModel):
    """Aggregated statistics for the Admin Dashboard"""
    active_members: int
    total_trainers: int
    upcoming_sessions: int
    total_revenue: float
    pending_payments: int
    equipment_issues: int
    revenue_today: float
    sessions_today: int

# --- ZAID'S SET FUNCTIONS ---
class MemberActivity(BaseModel):
    """UNION: Members who either attended or booked"""
    member_id: int
    activity: str                        # 'attendance' or 'booking'

class SimpleMemberId(BaseModel):
    """Generic model to return just a member_id for INTERSECT/EXCEPT queries"""
    member_id: int

# --- TRANSACTIONS ---
class AssignPlanRequest(BaseModel):
    """Transaction: Assign new plan and record payment simultaneously"""
    member_id: int
    plan_id: int
    amount: float
    payment_method: str

class TransferSessionRequest(BaseModel):
    """Transaction: Move a session from one trainer to another"""
    session_id: int
    new_trainer_id: int
    
# --- VIEWS ---
class MemberDashboardView(BaseModel):
    """Data returned from the vw_member_dashboard view"""
    member_id: int
    full_name: str
    plan_name: Optional[str] = None
    status: str
    total_paid: float
    total_visits: int

class SessionCapacityView(BaseModel):
    """Data returned from the vw_session_capacity view"""
    session_id: int
    session_name: str
    trainer: Optional[str] = None
    schedule_date: date
    max_capacity: int
    current_bookings: int
    spots_remaining: int
