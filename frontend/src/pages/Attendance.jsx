import { useEffect, useState } from 'react';
import { checkInMember, getAttendanceLog } from '../api/gymApi';

function Attendance() {
  const [log, setLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checkInId, setCheckInId] = useState('');

  // Fetch attendance log on page load
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getAttendanceLog();
        setLog(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching attendance", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Handle Check-In
  const handleCheckIn = async (e) => {
    e.preventDefault();
    if (!checkInId) return alert("Please enter a Member ID");

    try {
      await checkInMember(parseInt(checkInId));
      alert(`Member ${checkInId} checked in successfully! 🏋️‍♂️`);
      setCheckInId(''); // Clear input
      
      // Refresh the log to show the new check-in at the top
      const response = await getAttendanceLog();
      setLog(response.data);
      
    } catch (error) {
      alert("Failed to check in. Make sure the Member ID exists.");
      console.error(error);
    }
  };

  if (loading) return <div className="container mt-4"><h3>Loading Attendance...</h3></div>;

  // Filter today's check-ins for the highlight box
  const today = new Date().toLocaleDateString();
  const todayCheckIns = log.filter(entry => new Date(entry.check_in).toLocaleDateString() === today);

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Attendance Management</h2>

      <div className="row mb-4">
        {/* Check-In Form - Fixed: Removed bg-light, added proper dark styling */}
        <div className="col-md-4">
          <div className="card shadow-sm border-0" style={{ background: 'rgba(15, 20, 35, 0.9)', backdropFilter: 'blur(10px)' }}>
            <div className="card-body text-center">
              <h5 className="card-title mb-3" style={{ color: '#00ffff' }}>Member Check-In</h5>
              <form onSubmit={handleCheckIn}>
                <div className="mb-3">
                  <input 
                    type="number" 
                    className="form-control form-control-lg text-center" 
                    placeholder="Enter Member ID (e.g. 1)" 
                    value={checkInId}
                    onChange={(e) => setCheckInId(e.target.value)}
                    required 
                    style={{ 
                      background: 'rgba(0, 0, 0, 0.6)', 
                      border: '1px solid rgba(0, 255, 255, 0.3)',
                      color: 'white',
                      fontSize: '1.2rem'
                    }}
                  />
                </div>
                <button type="submit" className="btn btn-success btn-lg w-100">
                  <i className="fas fa-check-circle me-2"></i>✔ Check In
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Today's Stats - Fixed text color */}
        <div className="col-md-8">
          <div className="card shadow-sm border-0" style={{ 
            background: 'linear-gradient(135deg, #00aa55, #0088ff)',
            borderRadius: '16px'
          }}>
            <div className="card-body">
              <h5 className="card-title" style={{ color: 'white', opacity: 0.9 }}>Today's Activity</h5>
              <h1 className="display-4" style={{ color: 'white', fontWeight: 'bold' }}>{todayCheckIns.length}</h1>
              <p className="card-text" style={{ color: 'white', opacity: 0.8 }}>Total Check-Ins Today</p>
            </div>
          </div>
        </div>
      </div>

      {/* Full Attendance Log Table */}
      <h4 style={{ color: '#00ffff', marginBottom: '20px' }}>Recent Check-Ins</h4>
      <table className="table table-striped table-hover shadow-sm">
        <thead className="table-dark">
          <tr>
            <th>Log ID</th>
            <th>Member Name</th>
            <th>Check-In Time</th>
          </tr>
        </thead>
        <tbody>
          {log.map((entry) => (
            <tr key={entry.attendance_id}>
              <td>{entry.attendance_id}</td>
              <td>{entry.member}</td>
              <td>{new Date(entry.check_in).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Attendance;