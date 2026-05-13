import { useEffect, useState } from 'react';
import { getTrainers, registerTrainer } from '../api/gymApi';

function Trainers() {
  const [trainers, setTrainers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    specialization: '',
    phone: ''
  });

  // Fetch trainers on page load
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getTrainers();
        setTrainers(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching trainers", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Handle form input changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await registerTrainer(formData);
      alert("Trainer registered successfully! 🏋️‍♂️");
      
      // Reset form and hide it
      setFormData({ email: '', password: '', first_name: '', last_name: '', specialization: '', phone: '' });
      setShowForm(false);

      // Refresh the trainers list
      const response = await getTrainers();
      setTrainers(response.data);
      
    } catch (error) {
      console.error("Error registering trainer", error);
      alert("Failed to register trainer. Check console for details.");
    }
  };

  if (loading) return <div className="container mt-4"><h3>Loading Trainers...</h3></div>;

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Gym Trainers</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add New Trainer'}
        </button>
      </div>

      {/* REGISTER FORM */}
      {showForm && (
        <div className="card mb-4 shadow-sm">
          <div className="card-header bg-dark text-white">New Trainer Details</div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="row">
                <div className="col-md-4 mb-3">
                  <label className="form-label">First Name</label>
                  <input type="text" className="form-control" name="first_name" value={formData.first_name} onChange={handleChange} required />
                </div>
                <div className="col-md-4 mb-3">
                  <label className="form-label">Last Name</label>
                  <input type="text" className="form-control" name="last_name" value={formData.last_name} onChange={handleChange} required />
                </div>
                <div className="col-md-4 mb-3">
                  <label className="form-label">Specialization</label>
                  <input type="text" className="form-control" name="specialization" value={formData.specialization} onChange={handleChange} required />
                </div>
              </div>
              <div className="row">
                <div className="col-md-4 mb-3">
                  <label className="form-label">Email</label>
                  <input type="email" className="form-control" name="email" value={formData.email} onChange={handleChange} required />
                </div>
                <div className="col-md-4 mb-3">
                  <label className="form-label">Password</label>
                  <input type="password" className="form-control" name="password" value={formData.password} onChange={handleChange} required />
                </div>
                <div className="col-md-4 mb-3">
                  <label className="form-label">Phone</label>
                  <input type="text" className="form-control" name="phone" value={formData.phone} onChange={handleChange} />
                </div>
              </div>
              <button type="submit" className="btn btn-success mt-2">Add Trainer</button>
            </form>
          </div>
        </div>
      )}

      {/* TRAINERS TABLE */}
      <table className="table table-striped table-hover shadow-sm">
        <thead className="table-dark">
          <tr>
            <th>ID</th>
            <th>Full Name</th>
            <th>Specialization</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Hire Date</th>
          </tr>
        </thead>
        <tbody>
          {trainers.map((trainer) => (
            <tr key={trainer.trainer_id}>
              <td>{trainer.trainer_id}</td>
              <td>{trainer.full_name}</td>
              <td><span className="badge bg-info text-dark">{trainer.specialization}</span></td>
              <td>{trainer.email}</td>
              <td>{trainer.phone || 'N/A'}</td>
              <td>{new Date(trainer.hire_date).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Trainers;