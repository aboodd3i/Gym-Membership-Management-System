import { useEffect, useState } from 'react';
import { getMembers, getPlans, registerMember } from '../api/gymApi';

function Members() {
  const [members, setMembers] = useState([]);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false); // Toggle form visibility

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone: '',
    plan_id: ''
  });

  // Fetch members and plans on page load
  useEffect(() => {
    const fetchData = async () => {
      try {
        const membersRes = await getMembers();
        setMembers(membersRes.data);
        
        const plansRes = await getPlans();
        setPlans(plansRes.data);
        
        setLoading(false);
      } catch (error) {
        console.error("Error fetching data", error);
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
    e.preventDefault(); // Prevent page refresh
    try {
      await registerMember(formData);
      alert("Member registered successfully!");
      
      // Reset form and hide it
      setFormData({ email: '', password: '', first_name: '', last_name: '', phone: '', plan_id: '' });
      setShowForm(false);

      // Refresh the members list to show the new member
      const response = await getMembers();
      setMembers(response.data);
      
    } catch (error) {
      console.error("Error registering member", error);
      alert("Failed to register member. Check console for details.");
    }
  };

  if (loading) return <div className="container mt-4"><h3>Loading Members...</h3></div>;

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Gym Members</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Register New Member'}
        </button>
      </div>

      {/* REGISTER FORM - Only shows if showForm is true */}
      {showForm && (
        <div className="card mb-4 shadow-sm">
          <div className="card-header bg-dark text-white">New Member Details</div>
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
                  <label className="form-label">Email</label>
                  <input type="email" className="form-control" name="email" value={formData.email} onChange={handleChange} required />
                </div>
              </div>
              <div className="row">
                <div className="col-md-4 mb-3">
                  <label className="form-label">Password</label>
                  <input type="password" className="form-control" name="password" value={formData.password} onChange={handleChange} required />
                </div>
                <div className="col-md-4 mb-3">
                  <label className="form-label">Phone</label>
                  <input type="text" className="form-control" name="phone" value={formData.phone} onChange={handleChange} />
                </div>
                <div className="col-md-4 mb-3">
                  <label className="form-label">Membership Plan</label>
                  <select className="form-select" name="plan_id" value={formData.plan_id} onChange={handleChange} required>
                    <option value="">Select a Plan...</option>
                    {plans.map(plan => (
                      <option key={plan.plan_id} value={plan.plan_id}>
                        {plan.plan_name} - Rs. {plan.price}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <button type="submit" className="btn btn-success mt-2">Submit Registration</button>
            </form>
          </div>
        </div>
      )}

      {/* MEMBERS TABLE */}
      <table className="table table-striped table-hover shadow-sm">
        <thead className="table-dark">
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Phone</th>
            <th>Join Date</th>
            <th>Status</th>
            <th>Plan</th>
          </tr>
        </thead>
        <tbody>
          {members.map((member) => (
            <tr key={member.member_id}>
              <td>{member.member_id}</td>
              <td>{member.first_name} {member.last_name}</td>
              <td>{member.phone || 'N/A'}</td>
              <td>{new Date(member.join_date).toLocaleDateString()}</td>
              <td>
                <span className={`badge bg-${
                  member.status === 'active' ? 'success' : 
                  member.status === 'frozen' ? 'warning' : 
                  'danger'
                }`}>
                  {member.status}
                </span>
              </td>
              <td>{member.plan_name || 'No Plan'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Members;