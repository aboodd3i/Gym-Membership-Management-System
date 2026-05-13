import { useEffect, useState } from 'react';
import { getWorkouts, assignWorkout } from '../api/gymApi';

function Workouts() {
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    member_id: '',
    trainer_id: '',
    routine_description: '',
    performance_notes: ''
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getWorkouts();
        setWorkouts(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching workouts", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Assign a new workout
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await assignWorkout(formData);
      alert("Workout assigned successfully! 🏋️‍♂️");
      setFormData({ member_id: '', trainer_id: '', routine_description: '', performance_notes: '' });
      setShowForm(false);
      
      // Refresh the list
      const response = await getWorkouts();
      setWorkouts(response.data);
      
    } catch (error) {
      alert("Failed to assign workout. Check IDs and try again.");
      console.error(error);
    }
  };

  if (loading) return <div className="container mt-4"><h3>Loading Workouts...</h3></div>;

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Workout Tracking</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Assign Workout'}
        </button>
      </div>

      {/* ASSIGN WORKOUT FORM */}
      {showForm && (
        <div className="card mb-4 shadow-sm">
          <div className="card-header bg-dark text-white">Assign New Workout</div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="row">
                <div className="col-md-3 mb-3">
                  <label className="form-label">Member ID</label>
                  <input type="number" className="form-control" name="member_id" value={formData.member_id} onChange={handleChange} required />
                </div>
                <div className="col-md-3 mb-3">
                  <label className="form-label">Trainer ID</label>
                  <input type="number" className="form-control" name="trainer_id" value={formData.trainer_id} onChange={handleChange} required />
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">Routine Description</label>
                  <input type="text" className="form-control" name="routine_description" placeholder="e.g. Back and Biceps: Pull-ups 3x10..." value={formData.routine_description} onChange={handleChange} required />
                </div>
              </div>
              <div className="mb-3">
                <label className="form-label">Performance Notes (Optional)</label>
                <textarea className="form-control" name="performance_notes" rows="2" placeholder="e.g. Focus on slow negatives" value={formData.performance_notes} onChange={handleChange}></textarea>
              </div>
              <button type="submit" className="btn btn-success mt-2">Assign Workout</button>
            </form>
          </div>
        </div>
      )}

      {/* WORKOUT LOG TABLE */}
      <table className="table table-striped table-hover shadow-sm">
        <thead className="table-dark">
          <tr>
            <th>ID</th>
            <th>Date</th>
            <th>Member</th>
            <th>Trainer</th>
            <th>Routine</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {workouts.map(w => (
            <tr key={w.workout_id}>
              <td>{w.workout_id}</td>
              <td>{new Date(w.workout_date).toLocaleDateString()}</td>
              <td>{w.member}</td>
              <td>{w.trainer}</td>
              <td>{w.routine_description}</td>
              <td><i>{w.performance_notes || 'N/A'}</i></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Workouts;