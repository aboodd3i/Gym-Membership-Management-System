import { useEffect, useState } from 'react';
import { getMemberDashboardView, getSessionCapacityView } from '../api/gymApi';

function AdvancedAnalytics() {
  const [memberView, setMemberView] = useState([]);
  const [sessionView, setSessionView] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const memRes = await getMemberDashboardView();
        setMemberView(memRes.data);
        
        const sesRes = await getSessionCapacityView();
        setSessionView(sesRes.data);
        
        setLoading(false);
      } catch (error) {
        console.error("Error fetching analytics", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="container mt-4"><h3>Loading Analytics...</h3></div>;

  return (
    <div className="container mt-4">
      <h2 style={{ 
        background: 'linear-gradient(135deg, #00ffff, #ff2e00)',
        WebkitBackgroundClip: 'text',
        backgroundClip: 'text',
        color: 'transparent',
        marginBottom: '30px'
      }}>
        <i className="fas fa-chart-line me-2"></i>Advanced Analytics & DB Objects
      </h2>

      {/* TRIGGERS EXPLANATION - Fixed styling */}
      <div className="card mb-4 shadow-sm" style={{ 
        background: 'linear-gradient(135deg, #0a0a2a, #0f0f35)',
        border: '1px solid rgba(0, 255, 255, 0.3)',
        borderRadius: '20px'
      }}>
        <div className="card-body">
          <h5 className="card-title" style={{ color: '#00ffff', marginBottom: '20px' }}>
            <i className="fas fa-bolt me-2" style={{ color: '#ffcc00' }}></i>
            Active Database Triggers
          </h5>
          <p className="card-text" style={{ color: '#ccccdd', marginBottom: '20px' }}>
            The following logic runs automatically inside PostgreSQL, independent of the Python backend:
          </p>
          <div className="row">
            <div className="col-md-6 mb-3">
              <div className="card h-100" style={{ 
                background: 'rgba(0, 255, 255, 0.1)', 
                border: '1px solid rgba(0, 255, 255, 0.2)',
                borderRadius: '12px'
              }}>
                <div className="card-body">
                  <h6 style={{ color: '#00ff88', marginBottom: '10px' }}>
                    <i className="fas fa-credit-card me-2"></i>Trigger 1: Auto-Activate on Payment
                  </h6>
                  <p style={{ color: '#e0e0e0', fontSize: '0.9rem' }}>
                    If a frozen/inactive member makes a payment (status='paid'), their member status automatically changes to 'active'.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-6 mb-3">
              <div className="card h-100" style={{ 
                background: 'rgba(0, 255, 255, 0.1)', 
                border: '1px solid rgba(0, 255, 255, 0.2)',
                borderRadius: '12px'
              }}>
                <div className="card-body">
                  <h6 style={{ color: '#00ff88', marginBottom: '10px' }}>
                    <i className="fas fa-calendar-check me-2"></i>Trigger 2: Auto-Attendance on Session Completion
                  </h6>
                  <p style={{ color: '#e0e0e0', fontSize: '0.9rem' }}>
                    When a session booking status is updated to 'completed', an attendance check-in is automatically recorded.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* VIEW 1: Member Dashboard */}
      <h4 style={{ color: '#00ffff', marginBottom: '15px', marginTop: '30px' }}>
        <i className="fas fa-database me-2"></i>View: Member Dashboard (vw_member_dashboard)
      </h4>
      <p className="text-muted mb-3" style={{ color: '#aaaacc !important' }}>
        <i className="fas fa-info-circle me-1"></i>Pre-compiled query joining Members, Plans, Payments, and Attendance.
      </p>
      
      <div className="table-responsive">
        <table className="table table-striped table-hover shadow-sm mb-5" style={{ 
          background: 'rgba(10, 15, 30, 0.8)',
          borderRadius: '16px',
          overflow: 'hidden'
        }}>
          <thead style={{ background: 'linear-gradient(135deg, #0a0a1a, #12122a)' }}>
            <tr>
              <th style={{ color: '#00ffff', padding: '12px' }}>ID</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Full Name</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Plan</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Status</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Total Paid</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Total Visits</th>
            </tr>
          </thead>
          <tbody>
            {memberView.map(m => (
              <tr key={m.member_id}>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>{m.member_id}</td>
                <td style={{ color: '#e0e0e0', padding: '10px', fontWeight: '500' }}>{m.full_name}</td>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>{m.plan_name || 'None'}</td>
                <td style={{ padding: '10px' }}>
                  <span className={`badge`} style={{
                    background: m.status === 'active' ? 'linear-gradient(135deg, #00cc66, #009944)' : 
                                m.status === 'frozen' ? 'linear-gradient(135deg, #ffaa00, #ff7700)' : 
                                'linear-gradient(135deg, #ff3300, #cc2200)',
                    color: m.status === 'frozen' ? '#1a1a1a' : 'white',
                    padding: '5px 12px',
                    borderRadius: '20px'
                  }}>
                    {m.status}
                  </span>
                </td>
                <td style={{ color: '#00ff88', padding: '10px', fontWeight: 'bold' }}>Rs. {m.total_paid}</td>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>{m.total_visits}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* VIEW 2: Session Capacity */}
      <h4 style={{ color: '#00ffff', marginBottom: '15px', marginTop: '30px' }}>
        <i className="fas fa-chart-bar me-2"></i>View: Session Capacity (vw_session_capacity)
      </h4>
      <p className="text-muted mb-3" style={{ color: '#aaaacc !important' }}>
        <i className="fas fa-info-circle me-1"></i>Pre-compiled query calculating live booking capacity per session.
      </p>
      
      <div className="table-responsive">
        <table className="table table-striped table-hover shadow-sm" style={{ 
          background: 'rgba(10, 15, 30, 0.8)',
          borderRadius: '16px',
          overflow: 'hidden'
        }}>
          <thead style={{ background: 'linear-gradient(135deg, #0a0a1a, #12122a)' }}>
            <tr>
              <th style={{ color: '#00ffff', padding: '12px' }}>ID</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Session Name</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Trainer</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Date</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Max Capacity</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Booked</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Spots Remaining</th>
            </tr>
          </thead>
          <tbody>
            {sessionView.map(s => (
              <tr key={s.session_id}>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>{s.session_id}</td>
                <td style={{ color: '#e0e0e0', padding: '10px', fontWeight: '500' }}>{s.session_name}</td>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>{s.trainer}</td>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>{new Date(s.schedule_date).toLocaleDateString()}</td>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>{s.max_capacity}</td>
                <td style={{ color: '#ffaa00', padding: '10px', fontWeight: 'bold' }}>{s.current_bookings}</td>
                <td style={{ 
                  padding: '10px', 
                  fontWeight: 'bold',
                  color: s.spots_remaining === 0 ? '#ff4444' : '#00ff88'
                }}>
                  {s.spots_remaining}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdvancedAnalytics;
