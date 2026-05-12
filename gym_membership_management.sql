CREATE TABLE USERS(
	user_id SERIAL PRIMARY KEY,
	email VARCHAR(100) UNIQUE NOT NULL,
	password_hash VARCHAR(255) NOT NULL,
	role VARCHAR(20) NOT NULL CHECK (role IN('admin', 'trainer', 'member'))
);

CREATE TABLE MEMBERSHIP_PLANS (
	plan_id SERIAL PRIMARY KEY,
	plan_name VARCHAR(50) NOT NULL,
	duration_months INT NOT NULL,
	price DECIMAL(10,2) NOT NULL,
	description TEXT
);

CREATE TABLE MEMBERS (
	member_id SERIAL PRIMARY KEY,
	user_id INT UNIQUE NOT NULL REFERENCES USERS(user_id) ON DELETE CASCADE,
	first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50) NOT NULL,
	phone VARCHAR(15),
	join_date DATE NOT NULL DEFAULT CURRENT_DATE,
	plan_id INT REFERENCES MEMBERSHIP_PLANS(plan_id) ON DELETE SET NULL,
	status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'frozen'))
);

CREATE TABLE TRAINERS (
	trainer_id SERIAL PRIMARY KEY,
	user_id INT UNIQUE NOT NULL REFERENCES USERS(user_id) ON DELETE CASCADE,
	first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50) NOT NULL,
	specialization VARCHAR(100),
	hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
	phone VARCHAR(15)
);

CREATE TABLE PAYMENTS (
	payment_id SERIAL PRIMARY KEY,
	member_id INT NOT NULL REFERENCES MEMBERS(member_id) ON DELETE CASCADE,
	amount DECIMAL (10, 2) NOT NULL,
	payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
	payment_method  VARCHAR(50) DEFAULT 'cash',
	status VARCHAR(20) DEFAULT 'paid' CHECK (status IN ('paid', 'pending', 'overdue'))
);

CREATE TABLE SESSIONS (
	session_id SERIAL PRIMARY KEY,
	trainer_id INT NOT NULL REFERENCES TRAINERS(trainer_id) ON DELETE CASCADE,
	session_name VARCHAR(100) NOT NULL,
	schedule_date DATE NOT NULL DEFAULT CURRENT_DATE,
	start_time TIME NOT NULL DEFAULT CURRENT_TIME,
	end_time TIME NOT NULL DEFAULT CURRENT_TIME,
	max_capacity INT NOT NULL DEFAULT 20
);

CREATE TABLE SESSION_BOOKINGS (
	booking_id SERIAL PRIMARY KEY,
	session_id INT NOT NULL REFERENCES SESSIONS(session_id) ON DELETE CASCADE,
	member_id INT NOT NULL REFERENCES MEMBERS(member_id) ON DELETE CASCADE,
	booking_date DATE NOT NULL DEFAULT CURRENT_DATE,
	status VARCHAR(20) DEFAULT 'booked' CHECK (status IN ('booked', 'canceled', 'completed')),
	UNIQUE(session_id, member_id) -- to prevent double booking the same session 
);

CREATE TABLE ATTENDANCE(
	attendance_id SERIAL PRIMARY KEY,
	member_id INT NOT NULL REFERENCES MEMBERS(member_id) ON DELETE CASCADE,
	check_in TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE WORKOUTS (
	workout_id SERIAL PRIMARY KEY,
	member_id INT NOT NULL REFERENCES MEMBERS(member_id) ON DELETE CASCADE,
	trainer_id INT NOT NULL REFERENCES TRAINERS(trainer_id) ON DELETE SET NULL,
	workout_date DATE NOT NULL DEFAULT CURRENT_DATE,
	routine_description TEXT NOT NULL, -- what we did in the workout session
	performance_notes TEXT -- pr's etc
);

CREATE TABLE EQUIPMENT(
	equipment_id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	category VARCHAR(50),
	condition_status VARCHAR(20) DEFAULT 'good' CHECK (condition_status IN ('good', 'needs repair', 'broken')),
	purchase_date DATE,
	next_maintenance_date DATE
);

-- filling seed data to plot tables with dummmy values. 1 admin, 3 trainers, 5 members
INSERT INTO USERS (email, password_hash, role) VALUES
('saad.admin@gym.com', 'saad.admin123', 'admin'), -- basic format for username
('ali.trainer@gym.com', 'ali.trainer123', 'trainer'),
('zaid.trainer@gym.com', 'zaid.trainer123', 'trainer'),
('sara.trainer@gym.com', 'sara.trainer123', 'trainer'),
('abdullah.member@gym.com', 'abdullah.member123', 'member'),
('fatima.member@gym.com', 'fatima.member123', 'member'),
('bilal.member@gym.com', 'bilal.member123', 'member'),
('manahil.member@gym.com', 'manahil.member123', 'member'),
('asad.member@gym.com', 'asad.member123', 'member');

INSERT INTO MEMBERSHIP_PLANS (plan_name, duration_months, price, description) VALUES 
('Basic', 1, 3000.00, 'Access to gym floor only'),
('Standard', 3, 8000.00, 'Access to gym floor + 2 group classes per week'),
('Premium', 6, 15000.00, 'Unlimited group classes + 1 personal trainer session per week'),
('Annual', 12, 25000.00, 'Unlimited everything + custom diet plan');

INSERT INTO MEMBERS (user_id, first_name, last_name, phone, join_date, plan_id) VALUES
(5, 'Abdullah', 'Choudhry', '03456235788', '2024-10-01', 2),
(6, 'Fatima', 'Amjad', '03466255856', '2024-11-15', 2),
(7, 'Bilal', 'Khan', '03002425678', '2025-01-10', 2),
(8, 'Manahil', 'Mahmood', '03476878787', '2024-08-20', 2),
(9, 'Asad', 'Ahmed', '03214589843', '2025-10-06', 2);

INSERT INTO TRAINERS (user_id, first_name, last_name, specialization, hire_date, phone) VALUES
(2, 'Ali', 'Naqvi', 'Strength & Conditioning', '2023-05-01', '03459876543'),
(3, 'Zaid', 'Ahmed', 'Cardio & HIIT', '2023-08-15', '03459876543'),
(4, 'Sara', 'Khursheed', 'Yoga & Flexibility', '2024-01-10', '03459876543');

INSERT INTO PAYMENTS (member_id, amount, payment_date, payment_method, status) VALUES 
(1, 8000.00, '2024-10-01', 'Bank Transfer', 'paid'),
(2, 25000.00, '2024-11-15', 'Cash', 'paid'),
(3, 3000.00, '2025-01-10', 'Cash', 'paid'),
(4, 15000.00, '2024-08-20', 'Bank Transfer', 'paid'),
(5, 8000.00, '2025-10-06', 'Cash', 'pending'),
(1, 8000.00, '2024-11-01', 'Bank Transfer', 'paid') -- renewal for member 1

INSERT INTO sessions (trainer_id, session_name, schedule_date, start_time, end_time, max_capacity) VALUES 
(1, 'Heavy Lift Morning', '2026-09-15', '07:00:00', '08:30:00', 15),
(3, 'Power Yoga', '2026-09-15', '09:00:00', '10:00:00', 20),
(2, 'HIIT Blast', '2026-09-15', '17:00:00', '18:00:00', 25),
(1, 'Chest & Triceps', '2026-09-16', '19:00:00', '20:30:00', 10),
(3, 'Pilates', '2026-09-16', '17:00:00', '18:00:00', 25);


INSERT INTO session_bookings (session_id, member_id, status) VALUES 
(1, 1, 'booked'),
(2, 4, 'booked'),
(5, 2, 'booked'),
(3, 5, 'booked'), 
(4, 3, 'booked');

INSERT INTO attendance (member_id, check_in) VALUES 
(1, '2025-03-10 07:05:00'),
(1, '2025-03-12 07:00:00'),
(2, '2025-03-10 09:15:00'),
(3, '2025-03-12 17:05:00'),
(4, '2025-03-10 07:10:00'),
(5, '2025-03-12 17:00:00');

INSERT INTO workouts (member_id, trainer_id, workout_date, routine_description, performance_notes) VALUES 
(1, 1, '2025-03-10', 'Squats 3x8, Leg Press 3x10, Lunges 3x12', 'Good form, increase squat weight next time'),
(2, 3, '2025-03-10', 'Sun Salutations, Warrior Poses, Tree Pose', 'Excellent flexibility improvement'),
(3, 2, '2025-03-10', 'Burpees 4x15, Mountain Climbers 3x30, Planks 3x60s', 'High endurance, completed all sets'),
(4, 1, '2025-03-12', 'Bench Press 4x8, Cable Flies 3x12', 'Struggling on last set, keep same weight'),
(5, 3, '2025-03-12', 'Burpees 4x15, Mountain Climbers 3x30, Planks 3x60s', 'High endurance, completed all sets');

INSERT INTO equipment (name, category, condition_status, purchase_date, next_maintenance_date) VALUES 
('Treadmill Pro X', 'Cardio', 'broken', '2022-01-15', '2026-07-01'),
('Olympic Barbell Set', 'Strength', 'good', '2023-06-20', '2026-08-01'),
('Yoga Mats (Batch)', 'Flexibility', 'needs repair', '2022-11-01', '2026-08-01'), -- maintenance overdue
('Lat Pulldown Machine', 'Strength', 'good', '2023-03-10', '2026-09-01');

-- QUERIES

-- AUTHENTICATION N USER MANAFEMENT
-- Checks credentials and returns their role and specific ID
SELECT u.user_id, u.role, u.password_hash,
       m.member_id, m.first_name, m.last_name,
	   t.trainer_id, t.first_name, t.last_name
FROM users u
LEFT JOIN members m ON u.user_id = m.user_id
LEFT JOIN trainers t ON u.user_id = t.user_id
WHERE u.email = 'abdullah.member@gym.com'; -- change this to view member specific details

-- get all members
SELECT m.member_id, m.first_name, m.last_name, m.phone, m.join_date, m.status, mp.plan_name
FROM members m
LEFT JOIN membership_plans mp ON m.plan_id = mp.plan_id
ORDER BY m.join_date DESC;

-- update membership status
UPDATE members 
SET status = 'frozen'  -- change status here
WHERE member_id = 3; -- change this also 


-- TRAINER MANAGEMENT
-- get all trainers
SELECT t.trainer_id, t.first_name || ' ' || t.last_name AS full_name,
       t.specialization, t.hire_date, t.phone, u.email
FROM TRAINERS t
JOIN USERS u ON t.user_id = u.user_id
ORDER BY t.hire_date;

-- -- Get a trainer's full session schedule
SELECT s.session_name, s.schedule_date, s.start_time,
       s.end_time, s.max_capacity
FROM SESSIONS s
WHERE s.trainer_id = 1 -- change trainer id
ORDER BY s.schedule_date, s.start_time;

-- Count sessions per trainer
SELECT t.first_name || ' ' || t.last_name AS trainer,
       COUNT(s.session_id) AS total_sessions
FROM TRAINERS t
LEFT JOIN SESSIONS s ON t.trainer_id = s.trainer_id
GROUP BY t.trainer_id, t.first_name, t.last_name
ORDER BY total_sessions DESC;


-- MEMBERSHIP PLAN MANAGEMENT
-- get all plans 
SELECT plan_id, plan_name, duration_months, price, description 
FROM membership_plans
ORDER BY price ASC;

-- create new plan
INSERT INTO membership_plans (plan_name, duration_months, price, description) 
VALUES ('Student Discount', 4, 6000.00, 'Off-peak hours access for students'); -- change plan details accordingly can also make customs plans n shi


-- SESSION SCHEDULING AND BOOKING
-- get upcoming sessions to book 
SELECT s.session_id, s.session_name, s.schedule_date, s.start_time, s.end_time, s.max_capacity,
       t.first_name AS trainer_first_name, t.last_name AS trainer_last_name,
       COUNT(sb.booking_id) AS current_bookings
FROM sessions s
JOIN trainers t ON s.trainer_id = t.trainer_id
LEFT JOIN session_bookings sb ON s.session_id = sb.session_id AND sb.status = 'booked'
WHERE s.schedule_date >= CURRENT_DATE
GROUP BY s.session_id, t.trainer_id
ORDER BY s.schedule_date ASC, s.start_time ASC;

-- book a session (for members)
INSERT INTO session_bookings (session_id, member_id, status) 
VALUES (1, 1, 'booked'); -- change sesh id and mem id 

-- cancel  booking
UPDATE session_bookings 
SET status = 'cancelled' 
WHERE session_id = 1 AND member_id = 2; -- also change sesh id and mem id

-- mark a booking as completed
UPDATE SESSION_BOOKINGS SET status = 'completed'
WHERE session_id = 1 AND member_id = 1;

-- get a member's booked session (can be used for dashboard display)
SELECT s.session_name, s.schedule_date, s.start_time, s.end_time, 
       t.first_name AS trainer_name, sb.status
FROM session_bookings sb
JOIN sessions s ON sb.session_id = s.session_id
JOIN trainers t ON s.trainer_id = t.trainer_id
WHERE sb.member_id = 2 AND s.schedule_date >= CURRENT_DATE -- change member id
ORDER BY s.schedule_date ASC; 

-- All sessions a member has booked
SELECT s.session_name, s.schedule_date, s.start_time,
       t.first_name || ' ' || t.last_name AS trainer, sb.status
FROM SESSION_BOOKINGS sb
JOIN SESSIONS s ON sb.session_id = s.session_id
JOIN TRAINERS t ON s.trainer_id = t.trainer_id
WHERE sb.member_id = 1 -- change member id
ORDER BY s.schedule_date DESC;

-- All sessions with trainer name and spots remaining
SELECT s.session_id, s.session_name,
       t.first_name || ' ' || t.last_name AS trainer,
       s.schedule_date, s.start_time, s.end_time,
       s.max_capacity,
       s.max_capacity - COUNT(sb.booking_id) AS spots_remaining
FROM SESSIONS s
JOIN TRAINERS t ON s.trainer_id = t.trainer_id
LEFT JOIN SESSION_BOOKINGS sb
       ON s.session_id = sb.session_id AND sb.status = 'booked'
GROUP BY s.session_id, s.session_name, t.first_name,
         t.last_name, s.schedule_date, s.start_time,
         s.end_time, s.max_capacity
ORDER BY s.schedule_date, s.start_time;

-- All bookings for a specific session
SELECT sb.booking_id, m.first_name || ' ' || m.last_name AS member,
       sb.booking_date, sb.status
FROM SESSION_BOOKINGS sb
JOIN MEMBERS m ON sb.member_id = m.member_id
WHERE sb.session_id = 1; -- change sesh id

-- WORKOUT TRACKING
-- assign a workout
INSERT INTO workouts (member_id, trainer_id, routine_description, performance_notes) 
VALUES (1, 1, 'Back and Biceps: Pull-ups 3x10, Rows 3x12, Curls 3x15', 'Focus on slow negatives'); -- change mem id trainer id and description/notes

-- get a member's workout history
SELECT w.workout_date, w.routine_description, w.performance_notes,
       t.first_name AS trainer_first_name
FROM workouts w
LEFT JOIN trainers t ON w.trainer_id = t.trainer_id
WHERE w.member_id = 1
ORDER BY w.workout_date DESC
LIMIT 10;

-- Add a new workout log
INSERT INTO WORKOUTS (member_id, trainer_id, workout_date, routine_description, performance_notes)
VALUES (1, 1, CURRENT_DATE, 'Deadlift 4x6, Romanian DL 3x10', 'New PR on deadlift'); -- change details


-- All workout logs with member and trainer names
SELECT w.workout_id,
       m.first_name || ' ' || m.last_name AS member,
       t.first_name || ' ' || t.last_name AS trainer,
       w.workout_date, w.routine_description, w.performance_notes
FROM WORKOUTS w
JOIN MEMBERS m ON w.member_id = m.member_id
JOIN TRAINERS t ON w.trainer_id = t.trainer_id
ORDER BY w.workout_date DESC;

-- Workouts logged by a specific trainer
SELECT m.first_name || ' ' || m.last_name AS member,
       w.workout_date, w.routine_description, w.performance_notes
FROM WORKOUTS w
JOIN MEMBERS m ON w.member_id = m.member_id
WHERE w.trainer_id = 1 -- change trainer id
ORDER BY w.workout_date DESC;


-- ATTENDANCE MANAGEMENT
-- record check in
INSERT INTO attendance (member_id) 
VALUES (1); -- will auto assign an attendacne id and use default TIMESTAMP only change member id

-- Full attendance log with member names
SELECT a.attendance_id, m.first_name || ' ' || m.last_name AS member,
       a.check_in
FROM ATTENDANCE a
JOIN MEMBERS m ON a.member_id = m.member_id
ORDER BY a.check_in DESC;

-- Attendance count per member (most active members)
SELECT m.first_name || ' ' || m.last_name AS member,
       COUNT(a.attendance_id) AS total_visits
FROM ATTENDANCE a
JOIN MEMBERS m ON a.member_id = m.member_id
GROUP BY m.member_id, m.first_name, m.last_name
ORDER BY total_visits DESC;

-- Members who have never checked in (lazy ass people wasting their money)
SELECT m.first_name || ' ' || m.last_name AS member, u.email
FROM MEMBERS m
JOIN USERS u ON m.user_id = u.user_id
WHERE m.member_id NOT IN (
    SELECT DISTINCT member_id FROM ATTENDANCE
);

-- get member's attendance history
SELECT check_in 
FROM attendance 
WHERE member_id = 1 
ORDER BY check_in DESC;

-- get total attendace count for the day
SELECT COUNT(*) AS check_ins_today 
FROM attendance 
WHERE DATE(check_in) = CURRENT_DATE;


-- PAYMENT MANAGEMENT TO ESCAPE THE MATRIX
-- record a payment
INSERT INTO payments (member_id, amount, payment_method, status) 
VALUES (1, 3000.00, 'Cash', 'pending'); -- change details as required

-- get payment history for member
SELECT amount, payment_date, payment_method, status 
FROM payments 
WHERE member_id = 3
ORDER BY payment_date DESC;

-- All payments with member names
SELECT p.payment_id, m.first_name || ' ' || m.last_name AS member,
       p.amount, p.payment_date, p.payment_method, p.status
FROM PAYMENTS p
JOIN MEMBERS m ON p.member_id = m.member_id
ORDER BY p.payment_date DESC;

-- get all overdue payments
SELECT p.payment_id, m.first_name, m.last_name, p.amount, p.payment_date
FROM payments p
JOIN members m ON p.member_id = m.member_id
WHERE p.status IN ('pending', 'overdue')
ORDER BY p.payment_date ASC;

-- Revenue per payment method
SELECT payment_method,
       COUNT(*)     AS total_transactions,
       SUM(amount)  AS total_collected
FROM PAYMENTS
WHERE status = 'paid'
GROUP BY payment_method;

-- Calculates total revenue generated by each membership plan.
SELECT 
    mp.plan_name,
    COUNT(m.member_id) AS total_members,
    SUM(p.amount) AS total_revenue
FROM membership_plans mp
LEFT JOIN members m ON mp.plan_id = m.plan_id
LEFT JOIN payments p ON m.member_id = p.member_id AND p.status = 'paid'
GROUP BY mp.plan_name, mp.plan_id
ORDER BY total_revenue DESC;

-- gives revenue of last 6 months
SELECT 
    TO_CHAR(payment_date, 'YYYY-MM') AS month, 
    SUM(amount) AS total_revenue
FROM payments
WHERE status = 'paid' AND payment_date >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY TO_CHAR(payment_date, 'YYYY-MM')
ORDER BY month ASC;

-- mark an overdue/pending payment as paid
UPDATE payments 
SET status = 'paid' 
WHERE payment_id = 6; -- need to figure out how to automatically retreive the payment id 


-- EQUIPMENT MANAGEMENT
-- get all equipments
SELECT * FROM EQUIPMENT 
ORDER BY category, name;

-- Equipment needing attention (overdue or due soon)
SELECT name, category, condition_status,
       next_maintenance_date,
       next_maintenance_date - CURRENT_DATE AS days_until_maintenance
FROM EQUIPMENT
WHERE next_maintenance_date <= CURRENT_DATE + 30
ORDER BY next_maintenance_date;

-- update condition if an equipment is damaged or shi
UPDATE equipment 
SET condition_status = 'broken', next_maintenance_date = CURRENT_DATE 
WHERE equipment_id = 1;

-- update maintenance date after repair done
UPDATE equipment 
SET condition_status = 'Good', next_maintenance_date = CURRENT_DATE + INTERVAL '6 months' 
WHERE equipment_id = 1;


-- OTHER ADVANCED SHI LIKE ADMIN DASHBOARD N STUFF
-- For a specific member (e.g., member_id = 1), fetches their name, plan details, total payments made, and total check-ins.
SELECT 
    m.first_name || ' ' || m.last_name AS full_name,
    mp.plan_name,
    mp.duration_months,
    (SELECT SUM(amount) FROM payments WHERE member_id = m.member_id AND status = 'paid') AS total_paid,
    (SELECT COUNT(*) FROM attendance WHERE member_id = m.member_id) AS total_visits
FROM members m
JOIN membership_plans mp ON m.plan_id = mp.plan_id
WHERE m.member_id = 1;  -- change member id

-- Dashboard summary 
SELECT
    (SELECT COUNT(*) FROM MEMBERS WHERE status = 'active')    AS active_members,
    (SELECT COUNT(*) FROM TRAINERS)                           AS total_trainers,
    (SELECT COUNT(*) FROM SESSIONS
     WHERE schedule_date >= CURRENT_DATE)                     AS upcoming_sessions,
    (SELECT COALESCE(SUM(amount), 0) FROM PAYMENTS
     WHERE status = 'paid')                                   AS total_revenue,
    (SELECT COUNT(*) FROM PAYMENTS
     WHERE status IN ('pending','overdue'))                   AS pending_payments,
    (SELECT COUNT(*) FROM EQUIPMENT
     WHERE condition_status != 'good')                        AS equipment_issues;

-- gives gym stats to the admin (aka saddy daddy)
SELECT 
    (SELECT COUNT(*) FROM members WHERE status = 'active') AS active_members,
    (SELECT COUNT(*) FROM trainers) AS total_trainers,
    (SELECT SUM(amount) FROM payments WHERE status = 'paid' AND DATE(payment_date) = CURRENT_DATE) AS revenue_today,
    (SELECT COUNT(*) FROM sessions WHERE schedule_date = CURRENT_DATE) AS sessions_today;

-- Revenue per membership plan
SELECT mp.plan_name,
       COUNT(p.payment_id)  AS total_payments,
       SUM(p.amount)        AS total_revenue,
       AVG(p.amount)        AS avg_payment
FROM PAYMENTS p
JOIN MEMBERS m  ON p.member_id = m.member_id
JOIN MEMBERSHIP_PLANS mp ON m.plan_id = mp.plan_id
WHERE p.status = 'paid'
GROUP BY mp.plan_name
ORDER BY total_revenue DESC;

-- Lists all trainers, how many sessions they are conducting, and how many total members have booked those sessions.
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

-- Finds equipment that is either broken or has a maintenance date that is approaching/passed.
SELECT 
    name,
    category,
    condition_status,
    next_maintenance_date,
    CURRENT_DATE AS today,
    next_maintenance_date - CURRENT_DATE AS days_until_maintenance
FROM equipment
WHERE condition_status = 'broken' 
   OR next_maintenance_date <= CURRENT_DATE + INTERVAL '7 days'
ORDER BY days_until_maintenance ASC;

-- Members ranked by total amount paid
SELECT m.first_name || ' ' || m.last_name AS member,
       SUM(p.amount)   AS total_paid,
       COUNT(p.payment_id) AS num_payments
FROM PAYMENTS p
JOIN MEMBERS m ON p.member_id = m.member_id
WHERE p.status = 'paid'
GROUP BY m.member_id, m.first_name, m.last_name
ORDER BY total_paid DESC;

-- Sessions fill rate (how full each session is)
SELECT s.session_name, s.schedule_date,
       s.max_capacity,
       COUNT(sb.booking_id) AS booked,
       ROUND(COUNT(sb.booking_id) * 100 / s.max_capacity, 1) AS fill_pct
FROM SESSIONS s
LEFT JOIN SESSION_BOOKINGS sb
       ON s.session_id = sb.session_id AND sb.status = 'booked'
GROUP BY s.session_id, s.session_name, s.schedule_date, s.max_capacity
ORDER BY fill_pct DESC;


-- TRANSACTIONS 
-- Register a new member (user + member together)
BEGIN;

INSERT INTO USERS (email, password_hash, role)
VALUES ('omar.member@gym.com', 'omar.member123', 'member');

INSERT INTO MEMBERS (user_id, first_name, last_name, phone, join_date, plan_id)
VALUES (currval('users_user_id_seq'), 'Omar', 'Sheikh', '03001112233', CURRENT_DATE, 1);

COMMIT;

-- Register a new trainer (user + trainer together)
BEGIN;

INSERT INTO USERS (email, password_hash, role)
VALUES ('arsalan.trainer@gym.com', 'arsalan.trainer123', 'trainer');

INSERT INTO TRAINERS (user_id, first_name, last_name, specialization, hire_date, phone)
VALUES (currval('users_user_id_seq'), 'Arsalan', 'Rizvi', 'CrossFit', CURRENT_DATE, '03119988776');

COMMIT;

-- Member checks in for a session
BEGIN;

UPDATE SESSION_BOOKINGS 
SET status = 'completed' 
WHERE member_id = 1 AND session_id = 1;

INSERT INTO ATTENDANCE (member_id, check_in)
VALUES (1, CURRENT_TIMESTAMP);

COMMIT;

-- process overdue payments and freeze accounts
BEGIN;

UPDATE PAYMENTS 
SET status = 'overdue' 
WHERE status = 'pending' 
  AND payment_date < CURRENT_DATE - INTERVAL '30 days';

UPDATE MEMBERS 
SET status = 'frozen' 
WHERE member_id IN (
    SELECT DISTINCT member_id 
    FROM PAYMENTS 
    WHERE status = 'overdue'
) AND status = 'active';

COMMIT;

-- assign a new plan and records its payment
BEGIN;

UPDATE MEMBERS 
SET plan_id = 4 
WHERE member_id = 3;

INSERT INTO PAYMENTS (member_id, amount, payment_date, payment_method, status)
VALUES (3, 25000.00, CURRENT_DATE, 'Cash', 'paid');

COMMIT;

-- cancel a member's booking when the kamina deactivates 
BEGIN;

UPDATE MEMBERS 
SET status = 'inactive' 
WHERE member_id = 5;

UPDATE SESSION_BOOKINGS 
SET status = 'canceled'
WHERE member_id = 5 
  AND status = 'booked';

COMMIT;

-- transfer a session from one trainer to another
BEGIN;

UPDATE SESSIONS 
SET trainer_id = 2 
WHERE session_id = 1;

COMMIT;

-- delete a member's account permanently
BEGIN;

UPDATE SESSION_BOOKINGS SET status = 'canceled' WHERE member_id = 3;

DELETE FROM USERS 
WHERE user_id = (SELECT user_id FROM MEMBERS WHERE member_id = 3); 

COMMIT;


-- ZAID'S SET FUNCTIONS
-- UNION: Members who either checked in OR booked a session
SELECT member_id, 'attendance' AS activity FROM ATTENDANCE
UNION
SELECT member_id, 'booking'    AS activity FROM SESSION_BOOKINGS;

-- INTERSECT: Members who BOTH attended AND have a workout logged
SELECT member_id FROM ATTENDANCE
INTERSECT
SELECT member_id FROM WORKOUTS;

-- MINUS: Members with active memberships who have NEVER checked in (postgres uses EXCEPT instead of MINUS)
SELECT member_id FROM MEMBERS WHERE status = 'active'
EXCEPT
SELECT DISTINCT member_id FROM ATTENDANCE;

-- MINUS: Members who booked sessions but never completed one
SELECT member_id FROM SESSION_BOOKINGS WHERE status = 'booked'
EXCEPT
SELECT member_id FROM SESSION_BOOKINGS WHERE status = 'completed';

-- Arithmetic: Price breakdown per plan
SELECT plan_name,
       price                                          AS total_price,
       ROUND(price / duration_months, 2)              AS monthly_rate,
       ROUND(price * 0.10, 2)                         AS ten_pct_discount,
       ROUND(price - (price * 0.10), 2)               AS discounted_price
FROM MEMBERSHIP_PLANS;

-- Subquery: Members paying above average
SELECT m.first_name || ' ' || m.last_name AS member, p.amount
FROM PAYMENTS p
JOIN MEMBERS m ON p.member_id = m.member_id
WHERE p.amount > (SELECT AVG(amount) FROM PAYMENTS WHERE status = 'paid')
ORDER BY p.amount DESC;

-- Window: Rank members by attendance
SELECT m.first_name || ' ' || m.last_name AS member,
       COUNT(a.attendance_id) AS visits,
       RANK() OVER (ORDER BY COUNT(a.attendance_id) DESC) AS rank
FROM ATTENDANCE a
JOIN MEMBERS m ON a.member_id = m.member_id
GROUP BY m.member_id, m.first_name, m.last_name;

-- Window: Running total of revenue
SELECT payment_date, amount,
       SUM(amount) OVER (ORDER BY payment_date) AS running_total
FROM PAYMENTS
WHERE status = 'paid'
ORDER BY payment_date;




