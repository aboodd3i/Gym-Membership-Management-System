import { useEffect, useState } from 'react';
import { getSessionsWithSpots, bookSession } from '../api/gymApi';

function Sessions() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getSessionsWithSpots();
        setSessions(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching sessions", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Handle booking logic
  const handleBook = async (sessionId) => {
    // Since we don't have a login system yet, we'll simulate it by asking for the Member ID
    const memberId = window.prompt("Enter your Member ID to book (e.g., 1, 2, 3):");
    
    if (!memberId) return; // If they click cancel, stop

    try {
      await bookSession({ session_id: sessionId, member_id: parseInt(memberId) });
      alert("Session booked successfully! 🎉");
      
      // Refresh the sessions list to update the spots remaining
      const response = await getSessionsWithSpots();
      setSessions(response.data);
      
    } catch (error) {
      const errorMsg = error.response?.data?.detail || "Failed to book session.";
      alert(errorMsg); // Will show errors like "Session is full" or "Already booked"
    }
  };

  if (loading) return <div className="container mt-4"><h3>Loading Sessions...</h3></div>;

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Upcoming Sessions</h2>
      
      <div className="row">
                {sessions.map((session) => (
          <div className="col-md-4 mb-4" key={session.session_id}>
            <div className="card h-100 shadow-sm border-0">
              <div className="card-header bg-dark text-white">
                <h5 className="mb-0">{session.session_name}</h5>
              </div>
              <div className="card-body">
                <p className="card-text"><strong>Trainer:</strong> {session.trainer}</p>
                <p className="card-text"><strong>Date:</strong> {new Date(session.schedule_date).toLocaleDateString()}</p>
                <p className="card-text"><strong>Time:</strong> {session.start_time} - {session.end_time}</p>
                
                {/* Spots Remaining Indicator - Made Bulletproof */}
                <div className="mt-3">
                  <div className="d-flex justify-content-between mb-1">
                    <small>Capacity</small>
                    <small>{(session.max_capacity || 0) - (session.spots_remaining || 0)} / {session.max_capacity || 0} booked</small>
                  </div>
                  <div className="progress">
                    <div 
                      className={`progress-bar ${(session.spots_remaining || 0) === 0 ? 'bg-danger' : 'bg-success'}`} 
                      role="progressbar" 
                      style={{
                        width: `${(((session.max_capacity || 0) - (session.spots_remaining || 0)) / (session.max_capacity || 1)) * 100}%`
                      }}
                    ></div>
                  </div>
                  <p className="text-center mt-2 fw-bold text-primary">
                    {(session.spots_remaining || 0) === 0 ? 'CLASS FULL' : `${session.spots_remaining || 0} Spots Left`}
                  </p>
                </div>
              </div>
              <div className="card-footer bg-white border-top-0">
                <button 
                  className="btn btn-primary w-100" 
                  onClick={() => handleBook(session.session_id)}
                  disabled={(session.spots_remaining || 0) === 0} // Disable if full
                >
                  {(session.spots_remaining || 0) === 0 ? 'Sold Out' : 'Book Now'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Sessions;