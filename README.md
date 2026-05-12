# Gym and Fitness Membership Management API

This README documents the API routers and their views (endpoints). Database views and triggers are not defined in this repository.

## Routers and Views

### Authentication Router
Location: backend/apis/authentication/router.py

- POST /api/auth/login
  - Validates email and password, returns user role and member/trainer info.

### Members Router
Location: backend/apis/members/router.py

- GET /api/members
  - Returns all members with optional plan names.
- PATCH /api/members/{member_id}/status
  - Updates a member status (active, inactive, frozen).
- GET /api/members/{member_id}/dashboard
  - Aggregates a member dashboard with plan details, total paid, and total visits.

### Trainers Router
Location: backend/apis/trainers/router.py

- GET /api/trainers
  - Lists all trainers with contact and specialization details.
- GET /api/trainers/{trainer_id}/schedule
  - Returns all sessions assigned to a trainer.
- GET /api/trainers/session-count
  - Counts sessions per trainer.
- GET /api/trainers/workload
  - Returns trainer workload with sessions and booking totals.

### Membership Plans Router
Location: backend/apis/membership_plans/router.py

- GET /api/plans
  - Lists all membership plans ordered by price.
- POST /api/plans
  - Creates a new membership plan.

### Sessions Router
Location: backend/apis/sessions/router.py

- GET /api/sessions/upcoming
  - Lists upcoming sessions with current booking counts.
- GET /api/sessions/with-spots
  - Lists sessions with remaining capacity calculated.
- GET /api/sessions/fill-rate
  - Calculates and returns fill percentage for sessions.
- GET /api/sessions/{session_id}/bookings
  - Lists all bookings for a session.
- POST /api/sessions/book
  - Books a session for a member.
- PATCH /api/sessions/cancel-booking
  - Cancels a booking for a member.
- GET /api/members/{member_id}/sessions/upcoming
  - Lists a member upcoming sessions.
- GET /api/members/{member_id}/sessions/history
  - Lists a member session history (past and future).

### Workouts Router
Location: backend/apis/workouts/router.py

- POST /api/workouts
  - Logs a new workout for a member by a trainer.
- GET /api/workouts
  - Admin view of all workouts with member and trainer names.
- GET /api/members/{member_id}/workouts
  - Member view of their recent workouts.
- GET /api/trainers/{trainer_id}/workouts
  - Trainer view of workouts they assigned.

### Attendance Router
Location: backend/apis/attendance/router.py

- POST /api/attendance
  - Records a member check-in.
- GET /api/attendance
  - Admin view of all check-ins.
- GET /api/attendance/most-active
  - Lists members ranked by total visits.
- GET /api/attendance/lazy-members
  - Finds members who never checked in.
- GET /api/members/{member_id}/attendance
  - Member view of personal check-in history.
- GET /api/attendance/today-count
  - Returns count of check-ins for today.

### Payments Router
Location: backend/apis/payments/router.py

- POST /api/payments
  - Records a payment.
- GET /api/payments
  - Admin view of all payments.
- GET /api/members/{member_id}/payments
  - Member payment history.
- GET /api/payments/overdue
  - Payments pending or overdue.
- PATCH /api/payments/{payment_id}/mark-paid
  - Marks a payment as paid.
- GET /api/payments/revenue-by-method
  - Revenue grouped by payment method.
- GET /api/payments/revenue-by-plan
  - Revenue grouped by membership plan.
- GET /api/payments/detailed-revenue-by-plan
  - Detailed plan revenue stats.
- GET /api/payments/monthly-revenue
  - Monthly revenue for last 6 months.
- GET /api/payments/top-payers
  - Ranks top paying members.

### Equipment Router
Location: backend/apis/equipments/router.py

- GET /api/equipment
  - Lists all equipment.
- GET /api/equipment/maintenance-alerts
  - Lists equipment requiring maintenance or marked broken.
- PATCH /api/equipment/{equipment_id}/condition
  - Updates equipment condition.
- PATCH /api/equipment/{equipment_id}/repair-complete
  - Marks repair complete and schedules maintenance.

### Etc Router (Dashboard, Transactions, Analytics)
Location: backend/apis/etc/router.py

Dashboard
- GET /api/dashboard/stats
  - Returns dashboard summary statistics.

Transactions
- POST /api/transactions/register-member
  - Registers a user and member in one transaction.
- POST /api/transactions/register-trainer
  - Registers a user and trainer in one transaction.
- POST /api/transactions/check-in-session
  - Marks a booking completed and logs attendance.
- POST /api/transactions/process-overdue
  - Marks overdue payments and freezes member accounts.
- POST /api/transactions/assign-plan
  - Assigns a plan and records payment.
- PATCH /api/transactions/deactivate-member/{member_id}
  - Deactivates a member and cancels bookings.
- PATCH /api/transactions/transfer-session
  - Transfers a session to another trainer.
- DELETE /api/transactions/delete-member/{member_id}
  - Deletes a member account and cancels bookings.

Advanced Analytics
- GET /api/analytics/member-activity-union
  - Union of members who attended or booked sessions.
- GET /api/analytics/active-members-intersect
  - Intersect of members who attended and logged workouts.
- GET /api/analytics/absent-active-members
  - Active members who never checked in.
- GET /api/analytics/incomplete-bookings
  - Members with booked but incomplete sessions.
- GET /api/plans/pricing-breakdown
  - Plan pricing breakdown with discounts.
- GET /api/payments/above-average
  - Payments above average amount.
- GET /api/analytics/attendance-ranking
  - Rank members by attendance.
- GET /api/analytics/revenue-running-total
  - Running total of paid revenue over time.
