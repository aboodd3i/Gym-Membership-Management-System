import { useEffect, useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { getTrainerAssignedWorkouts, assignWorkout } from '../api/gymApi';

function TrainerWorkouts() {
  const { user } = useContext(AuthContext);
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const [formData, setFormData] = useState({ member_id: '', routine_description: '', performance_notes: '' });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getTrainerAssignedWorkouts(user.trainer_id);
        setWorkouts(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching workouts", error);
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await assignWorkout({ 
        ...formData, 
        trainer_id: user.trainer_id // Automatically use logged-in trainer's ID
      });
      alert("Workout assigned successfully! 🏋️‍♂️");
      setFormData({ member_id: '', routine_description: '', performance_notes: '' });
      setShowForm(false);
      
      const response = await getTrainerAssignedWorkouts(user.trainer_id);
      setWorkouts(response.data);
    } catch (error) {
      alert("Failed to assign workout. Check Member ID.");
    }
  };

  if (loading) return <div className="container mt-4"><h3>Loading Workouts...</h3></div>;

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Manage Workouts</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Assign Workout'}
        </button>
      </div>

      {showForm && (
        <div className="card mb-4 shadow-sm">
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="row">
                <div className="col-md-4 mb-3">
                  <label className="form-label">Member ID</label>
                  <input type="number" className="form-control" name="member_id" value={formData.member_id} onChange={(e) => setFormData({...formData, member_id: e.target.value})} required />
                </div>
                <div className="col-md-8 mb-3">
                  <label className="form-label">Routine Description</label>
                  <input type="text" className="form-control" name="routine_description" value={formData.routine_description} onChange={(e) => setFormData({...formData, routine_description: e.target.value})} required />
                </div>
              </div>
              <button type="submit" className="btn btn-success">Assign</button>
            </form>
          </div>
        </div>
      )}

      <table className="table table-striped table-hover shadow-sm">
        <thead className="table-dark">
          <tr>
            <th>Date</th>
            <th>Member ID</th>
            <th>Routine</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {workouts.map(w => (
            <tr key={w.workout_id}>
              <td>{new Date(w.workout_date).toLocaleDateString()}</td>
              <td>{w.member_id}</td> {/* Note: you might need to join member name in backend if you want their name here */}
              <td>{w.routine_description}</td>
              <td><i>{w.performance_notes || 'N/A'}</i></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TrainerWorkouts;