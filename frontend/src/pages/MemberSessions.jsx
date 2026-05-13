import { useEffect, useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { getSessionsWithSpots, bookSession } from '../api/gymApi';

function MemberSessions() {
  const { user } = useContext(AuthContext);
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

  const handleBook = async (sessionId) => {
    try {
      // Automatically use the logged-in member's ID!
      await bookSession({ session_id: sessionId, member_id: user.member_id });
      alert("Session booked successfully! 🎉");
      
      // Refresh sessions to update spots
      const response = await getSessionsWithSpots();
      setSessions(response.data);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || "Failed to book session.";
      alert(errorMsg); // Shows "Already booked" or "Session is full"
    }
  };

  if (loading) return <div className="container mt-4"><h3>Loading Sessions...</h3></div>;

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Book a Session</h2>
      <div className="row">
        {sessions.map((session) => (
          <div className="col-md-4 mb-4" key={session.session_id}>
            <div className="card h-100 shadow-sm border-0">
              <div className="card-header bg-dark text-white">
                <h5 className="mb-0">{session.session_name}</h5>
              </div>
              <div className="card-body">
                <p><strong>Trainer:</strong> {session.trainer}</p>
                <p><strong>Date:</strong> {new Date(session.schedule_date).toLocaleDateString()}</p>
                <p><strong>Time:</strong> {session.start_time} - {session.end_time}</p>
                <p className="fw-bold text-primary">
                  {session.spots_remaining <= 0 ? 'CLASS FULL' : `${session.spots_remaining} Spots Left`}
                </p>
              </div>
              <div className="card-footer bg-white border-top-0">
                <button 
                  className="btn btn-primary w-100" 
                  onClick={() => handleBook(session.session_id)}
                  disabled={session.spots_remaining <= 0}
                >
                  {session.spots_remaining <= 0 ? 'Sold Out' : 'Book Now'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MemberSessions;