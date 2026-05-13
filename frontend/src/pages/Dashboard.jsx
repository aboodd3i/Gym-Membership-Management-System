import { useEffect, useState } from 'react';
import { getDashboardStats } from '../api/gymApi';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch data from our Python backend
    const fetchData = async () => {
      try {
        const response = await getDashboardStats();
        setStats(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching dashboard data", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="container mt-5"><h2>Loading Dashboard...</h2></div>;
  if (!stats) return <div className="container mt-5"><h2>Failed to load data.</h2></div>;

      return (
    <div className="container mt-5">
      <h2 className="mb-4 fw-bold">Admin Dashboard</h2>
      
      <div className="row">
        {/* Card 1 */}
        <div className="col-md-3">
          <div className="card text-white bg-gradient-primary mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-users fa-2x opacity-75"></i></div>
              <div>
                <h6 className="card-subtitle mb-1 text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>Active Members</h6>
                <h2 className="card-title mb-0 fw-bold">{stats.active_members}</h2>
              </div>
            </div>
          </div>
        </div>

        {/* Card 2 */}
        <div className="col-md-3">
          <div className="card text-white bg-gradient-success mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-money-bill-wave fa-2x opacity-75"></i></div>
              <div>
                <h6 className="card-subtitle mb-1 text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>Revenue Today</h6>
                <h2 className="card-title mb-0 fw-bold">Rs. {stats.revenue_today}</h2>
              </div>
            </div>
          </div>
        </div>

        {/* Card 3 */}
        <div className="col-md-3">
          <div className="card text-white bg-gradient-warning mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-calendar-check fa-2x opacity-75"></i></div>
              <div>
                <h6 className="card-subtitle mb-1 text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>Sessions Today</h6>
                <h2 className="card-title mb-0 fw-bold">{stats.sessions_today}</h2>
              </div>
            </div>
          </div>
        </div>

        {/* Card 4 */}
        <div className="col-md-3">
          <div className="card text-white bg-gradient-danger mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-exclamation-triangle fa-2x opacity-75"></i></div>
              <div>
                <h6 className="card-subtitle mb-1 text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>Equipment Issues</h6>
                <h2 className="card-title mb-0 fw-bold">{stats.equipment_issues}</h2>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Second Row */}
      <div className="row">
        <div className="col-md-4">
          <div className="card text-white bg-gradient-info mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-dumbbell fa-2x opacity-75"></i></div>
              <div>
                <h6 className="card-subtitle mb-1 text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>Total Trainers</h6>
                <h2 className="card-title mb-0 fw-bold">{stats.total_trainers}</h2>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card text-white bg-gradient-secondary mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-list-ul fa-2x opacity-75"></i></div>
              <div>
                <h6 className="card-subtitle mb-1 text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>Upcoming Sessions</h6>
                <h2 className="card-title mb-0 fw-bold">{stats.upcoming_sessions}</h2>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card text-white bg-gradient-light mb-4">
            <div className="card-body d-flex align-items-center">
              <div className="me-4"><i className="fas fa-piggy-bank fa-2x opacity-75"></i></div>
              <div>
                <h6 className="card-subtitle mb-1 text-uppercase" style={{fontSize: '0.8rem', letterSpacing: '1px'}}>All-Time Revenue</h6>
                <h2 className="card-title mb-0 fw-bold">Rs. {stats.total_revenue}</h2>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;