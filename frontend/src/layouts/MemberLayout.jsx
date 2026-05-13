import { useContext } from 'react';
import { Link, Outlet } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

function MemberLayout() {
  const { user, logout } = useContext(AuthContext);

  return (
    <>
      <nav className="navbar navbar-expand-lg navbar-dark sticky-top nav-gradient bg-gradient-success">
        <div className="container-fluid">
          <Link className="navbar-brand fw-bold fs-4" to="/member">
            <i className="fas fa-bolt me-2"></i>FAST GYM (Member)
          </Link>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item"><Link className="nav-link" to="/member"><i className="fas fa-home me-1"></i>Dashboard</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/member/sessions"><i className="fas fa-calendar-alt me-1"></i>Book Sessions</Link></li>
              <li className="nav-item d-flex align-items-center me-3">
                <span className="text-light fw-bold"><i className="fas fa-user me-1"></i>{user?.member_first_name}</span>
              </li>
              <li className="nav-item">
                <button onClick={logout} className="btn btn-outline-light btn-sm fw-bold"><i className="fas fa-sign-out-alt me-1"></i> Logout</button>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      <Outlet /> {/* This renders the MemberDashboard or other member pages */}
    </>
  );
}

export default MemberLayout;