import { useEffect, useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { getMemberDashboard } from '../api/gymApi';

function MemberDashboard() {
  const { user } = useContext(AuthContext);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (user?.member_id) {
      const fetchData = async () => {
        try {
          const response = await getMemberDashboard(user.member_id);
          setStats(response.data);
        } catch (error) {
          console.error("Error fetching member dashboard", error);
        }
      };
      fetchData();
    }
  }, [user]);

  if (!stats) return <div className="container mt-5"><h3>Loading your dashboard...</h3></div>;

  return (
    <div className="container mt-5">
      <h2 className="mb-4 fw-bold">Welcome back, {stats.full_name}! 💪</h2>
      
      <div className="row">
        <div className="col-md-4">
          <div className="card text-white bg-gradient-primary mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-id-card fa-2x opacity-75"></i></div>
              <div>
                <h6 className="text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>Current Plan</h6>
                <h3 className="mb-0 fw-bold">{stats.plan_name}</h3>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card text-white bg-gradient-success mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-wallet fa-2x opacity-75"></i></div>
              <div>
                <h6 className="text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>Total Paid</h6>
                <h3 className="mb-0 fw-bold">Rs. {stats.total_paid}</h3>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card text-white bg-gradient-info mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-walking fa-2x opacity-75"></i></div>
              <div>
                <h6 className="text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>Total Visits</h6>
                <h3 className="mb-0 fw-bold">{stats.total_visits}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MemberDashboard;