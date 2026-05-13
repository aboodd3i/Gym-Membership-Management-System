import { useEffect, useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

function TrainerDashboard() {
  const { user } = useContext(AuthContext);
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Make sure user and trainer_id exist before fetching
    if (user?.trainer_id) {
      const fetchData = async () => {
        try {
          const response = await getTrainerSchedule(user.trainer_id);
          setSchedule(response.data);
          setLoading(false);
        } catch (error) {
          console.error("Error fetching trainer schedule", error);
          setLoading(false);
        }
      };
      fetchData();
    }
  }, [user]);

  if (loading) return <div className="container mt-5"><h3>Loading your schedule...</h3></div>;

  return (
    <div className="container mt-5">
      <h2 className="mb-4 fw-bold">Welcome back, {user?.trainer_first_name}! 🏋️‍♂️</h2>
      
      <div className="row">
        <div className="col-md-6">
          <div className="card text-white bg-gradient-danger mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-calendar-check fa-2x opacity-75"></i></div>
              <div>
                <h6 className="text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>Your Schedule</h6>
                <h3 className="mb-0 fw-bold">{schedule.length} Upcoming Sessions</h3>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card text-white bg-gradient-info mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-clipboard-list fa-2x opacity-75"></i></div>
              <div>
                <h6 className="text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>Workout Logs</h6>
                <h3 className="mb-0 fw-bold">Manage Routines</h3>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Trainer Schedule Table */}
      <h4 className="mt-4">Your Upcoming Sessions</h4>
      <table className="table table-striped table-hover shadow-sm mt-2">
        <thead className="table-dark">
          <tr>
            <th>Session Name</th>
            <th>Date</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Max Capacity</th>
          </tr>
        </thead>
        <tbody>
          {schedule.length === 0 ? (
            <tr><td colSpan="5" className="text-center">No upcoming sessions scheduled.</td></tr>
          ) : (
            schedule.map(session => (
              <tr key={session.session_id}>
                <td>{session.session_name}</td>
                <td>{new Date(session.schedule_date).toLocaleDateString()}</td>
                <td>{session.start_time}</td>
                <td>{session.end_time}</td>
                <td>{session.max_capacity}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default TrainerDashboard;