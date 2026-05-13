import { useContext } from 'react';
import { Link, Outlet, Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

function AdminLayout() {
  const { user, logout } = useContext(AuthContext);

  // If someone navigates here and isn't an admin, kick them out
  if (user?.role !== 'admin') return <Navigate to="/login" />;

  return (
    <>
      {/* Admin Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark sticky-top nav-gradient">
        <div className="container-fluid">
          <Link className="navbar-brand fw-bold fs-4" to="/admin">
            <i className="fas fa-bolt me-2"></i>FAST GYM (Admin)
          </Link>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item"><Link className="nav-link" to="/admin"><i className="fas fa-home me-1"></i>Dashboard</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/admin/members"><i className="fas fa-users me-1"></i>Members</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/admin/trainers"><i className="fas fa-dumbbell me-1"></i>Trainers</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/admin/sessions"><i className="fas fa-calendar-alt me-1"></i>Sessions</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/admin/attendance"><i className="fas fa-walking me-1"></i>Attendance</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/admin/workouts"><i className="fas fa-clipboard-list me-1"></i>Workouts</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/admin/equipment"><i className="fas fa-tools me-1"></i>Equipment</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/admin/payments"><i className="fas fa-credit-card me-1"></i>Payments</Link></li>
              <li className="nav-item"><Link className="nav-link text-warning fw-bold" to="/admin/analytics"><i className="fas fa-chart-pie me-1"></i>Analytics</Link></li>
              
              {/* Logout Button (Preserved your custom styling!) */}
              <li className="nav-item ms-3">
                <button 
                  onClick={logout} 
                  className="btn btn-sm fw-bold" 
                  style={{
                    background: 'linear-gradient(135deg, #ff2e00, #ff7700)',
                    border: 'none',
                    color: 'white',
                    padding: '6px 16px',
                    borderRadius: '30px',
                    fontFamily: 'Orbitron, monospace',
                    letterSpacing: '0.5px',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 0 20px rgba(255, 46, 0, 0.4)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = 'none';
                  }}
                >
                  <i className="fas fa-sign-out-alt me-1"></i> Logout
                </button>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      {/* This renders the child route (Dashboard, Members, etc.) */}
      <Outlet /> 
    </>
  );
}

export default AdminLayout;
