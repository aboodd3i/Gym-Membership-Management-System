import { useContext } from 'react';
import { Link, Outlet } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

function TrainerLayout() {
  const { user, logout } = useContext(AuthContext);

  return (
    <>
      <nav className="navbar navbar-expand-lg navbar-dark sticky-top nav-gradient bg-gradient-danger">
        <div className="container-fluid">
          <Link className="navbar-brand fw-bold fs-4" to="/trainer">
            <i className="fas fa-bolt me-2"></i>FAST GYM (Trainer)
          </Link>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item"><Link className="nav-link" to="/trainer"><i className="fas fa-home me-1"></i>Dashboard</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/trainer/workouts"><i className="fas fa-clipboard-list me-1"></i>Manage Workouts</Link></li>
              <li className="nav-item d-flex align-items-center me-3">
                <span className="text-light fw-bold"><i className="fas fa-dumbbell me-1"></i>{user?.trainer_first_name}</span>
              </li>
              <li className="nav-item">
                <button onClick={logout} className="btn btn-outline-light btn-sm fw-bold"><i className="fas fa-sign-out-alt me-1"></i> Logout</button>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      <Outlet />
    </>
  );
}

export default TrainerLayout;