import axios from 'axios';

// Point this to your FastAPI server URL
const API_BASE_URL = 'http://localhost:8000/api';

// Fetch dashboard stats
export const getDashboardStats = () => axios.get(`${API_BASE_URL}/dashboard/stats`);

// Fetch all members
export const getMembers = () => axios.get(`${API_BASE_URL}/members`);

// Fetch all membership plans (for the dropdown)
export const getPlans = () => axios.get(`${API_BASE_URL}/plans`);

// Register a new member (The Transaction!)
export const registerMember = (memberData) => axios.post(`${API_BASE_URL}/transactions/register-member`, memberData);

// Fetch upcoming sessions with spots remaining
export const getSessionsWithSpots = () => axios.get(`${API_BASE_URL}/sessions/with-spots`);

// Book a session for a member
export const bookSession = (bookingData) => axios.post(`${API_BASE_URL}/sessions/book`, bookingData);

// Fetch all trainers
export const getTrainers = () => axios.get(`${API_BASE_URL}/trainers`);

// Register a new trainer (The Transaction!)
export const registerTrainer = (trainerData) => axios.post(`${API_BASE_URL}/transactions/register-trainer`, trainerData);

// Record a check-in
export const checkInMember = (memberId) => axios.post(`${API_BASE_URL}/attendance`, { member_id: memberId });

// Get full attendance log
export const getAttendanceLog = () => axios.get(`${API_BASE_URL}/attendance`);

// Fetch all equipment
export const getEquipment = () => axios.get(`${API_BASE_URL}/equipment`);

// Fetch maintenance alerts
export const getMaintenanceAlerts = () => axios.get(`${API_BASE_URL}/equipment/maintenance-alerts`);

// Update equipment condition (e.g., mark as broken)
export const updateEquipmentCondition = (equipmentId, conditionData) => 
    axios.patch(`${API_BASE_URL}/equipment/${equipmentId}/condition`, conditionData);

// Mark equipment as repaired
export const repairEquipment = (equipmentId) => 
    axios.patch(`${API_BASE_URL}/equipment/${equipmentId}/repair-complete`);

// Fetch all payments
export const getPayments = () => axios.get(`${API_BASE_URL}/payments`);

// Fetch overdue/pending payments
export const getOverduePayments = () => axios.get(`${API_BASE_URL}/payments/overdue`);

// Record a new payment
export const recordPayment = (paymentData) => axios.post(`${API_BASE_URL}/payments`, paymentData);

// Mark a specific payment as paid
export const markPaymentPaid = (paymentId) => axios.patch(`${API_BASE_URL}/payments/${paymentId}/mark-paid`);

// Process all overdue accounts (The Transaction to freeze members!)
export const processOverdueAccounts = () => axios.post(`${API_BASE_URL}/transactions/process-overdue`);

// Fetch all workout logs
export const getWorkouts = () => axios.get(`${API_BASE_URL}/workouts`);

// Assign a new workout (Trainer to Member)
export const assignWorkout = (workoutData) => axios.post(`${API_BASE_URL}/workouts`, workoutData);

// Fetch Member Dashboard View
export const getMemberDashboardView = () => axios.get(`${API_BASE_URL}/analytics/member-dashboard-view`);

// Fetch Session Capacity View
export const getSessionCapacityView = () => axios.get(`${API_BASE_URL}/analytics/session-capacity-view`);

// Login user
export const loginUser = (credentials) => axios.post(`${API_BASE_URL}/auth/login`, credentials);

// Fetch member dashboard stats
export const getMemberDashboard = (memberId) => axios.get(`${API_BASE_URL}/members/${memberId}/dashboard`);

// Fetch a trainer's upcoming schedule
export const getTrainerSchedule = (trainerId) => axios.get(`${API_BASE_URL}/trainers/${trainerId}/schedule`);

// Fetch workouts assigned by a specific trainer
export const getTrainerAssignedWorkouts = (trainerId) => axios.get(`${API_BASE_URL}/trainers/${trainerId}/workouts`);
