import { useEffect, useState } from 'react';
import { getPayments, getOverduePayments, recordPayment, markPaymentPaid, processOverdueAccounts } from '../api/gymApi';

function Payments() {
  const [payments, setPayments] = useState([]);
  const [overduePayments, setOverduePayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    member_id: '',
    amount: '',
    payment_method: 'Cash',
    status: 'paid'
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const payRes = await getPayments();
        setPayments(payRes.data);
        
        const overRes = await getOverduePayments();
        setOverduePayments(overRes.data);
        
        setLoading(false);
      } catch (error) {
        console.error("Error fetching payments", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Record a new payment
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await recordPayment(formData);
      alert("Payment recorded successfully! 💰");
      setFormData({ member_id: '', amount: '', payment_method: 'Cash', status: 'paid' });
      setShowForm(false);
      refreshData();
    } catch (error) {
      alert("Failed to record payment.");
      console.error(error);
    }
  };

  // Mark a specific payment as paid
  const handleMarkPaid = async (paymentId) => {
    try {
      await markPaymentPaid(paymentId);
      alert("Payment marked as paid! ✅");
      refreshData();
    } catch (error) {
      alert("Failed to update payment.");
    }
  };

  // Run the transaction: Mark old payments as overdue & freeze members
  const handleProcessOverdue = async () => {
    if (window.confirm("Are you sure? This will freeze accounts with pending payments older than 30 days!")) {
      try {
        await processOverdueAccounts();
        alert("Overdue accounts processed! Frozen members updated. ❄️");
        refreshData();
      } catch (error) {
        alert("Failed to process overdue accounts.");
      }
    }
  };

  // Refresh data helper
  const refreshData = async () => {
    const payRes = await getPayments();
    setPayments(payRes.data);
    const overRes = await getOverduePayments();
    setOverduePayments(overRes.data);
  };

  if (loading) return <div className="container mt-4"><h3>Loading Finances...</h3></div>;

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Payments & Finance</h2>
        <div>
          <button className="btn btn-outline-danger me-2" onClick={handleProcessOverdue}>
            <i className="fas fa-snowflake me-2"></i>❄️ Process Overdue Accounts
          </button>
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? <><i className="fas fa-times me-2"></i>Cancel</> : <><i className="fas fa-plus me-2"></i>Record Payment</>}
          </button>
        </div>
      </div>

      {/* OVERDUE ALERTS SECTION - Fixed styling */}
      {overduePayments.length > 0 && (
        <div className="mb-4">
          <h4 className="text-danger" style={{ color: '#ff6600 !important', textShadow: '0 0 5px rgba(255, 102, 0, 0.5)' }}>
            <i className="fas fa-exclamation-triangle me-2"></i>
            Pending / Overdue Payments ({overduePayments.length})
          </h4>
          <div className="table-responsive">
            <table className="table" style={{ 
              background: 'rgba(255, 51, 0, 0.15)', 
              borderRadius: '16px',
              overflow: 'hidden'
            }}>
              <thead style={{ background: 'linear-gradient(135deg, #8B0000, #CC3300)' }}>
                <tr>
                  <th style={{ color: 'white', padding: '12px', fontFamily: 'Orbitron, monospace' }}>Payment ID</th>
                  <th style={{ color: 'white', padding: '12px', fontFamily: 'Orbitron, monospace' }}>Member</th>
                  <th style={{ color: 'white', padding: '12px', fontFamily: 'Orbitron, monospace' }}>Amount</th>
                  <th style={{ color: 'white', padding: '12px', fontFamily: 'Orbitron, monospace' }}>Date</th>
                  <th style={{ color: 'white', padding: '12px', fontFamily: 'Orbitron, monospace' }}>Status</th>
                  <th style={{ color: 'white', padding: '12px', fontFamily: 'Orbitron, monospace' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {overduePayments.map(p => (
                  <tr key={p.payment_id} style={{ background: 'rgba(255, 51, 0, 0.1)' }}>
                    <td style={{ color: '#ffaa88', padding: '10px', fontWeight: 'bold' }}>{p.payment_id}</td>
                    <td style={{ color: '#ffccaa', padding: '10px' }}>{p.member}</td>
                    <td style={{ color: '#ffcc88', padding: '10px', fontWeight: 'bold' }}>Rs. {p.amount}</td>
                    <td style={{ color: '#ffccaa', padding: '10px' }}>{new Date(p.payment_date).toLocaleDateString()}</td>
                    <td style={{ padding: '10px' }}>
                      <span className="badge" style={{ 
                        background: p.status === 'overdue' ? 'linear-gradient(135deg, #ff3300, #cc0000)' : 'linear-gradient(135deg, #ffaa00, #ff7700)',
                        color: 'white',
                        padding: '5px 12px',
                        borderRadius: '20px'
                      }}>
                        {p.status}
                      </span>
                    </td>
                    <td style={{ padding: '10px' }}>
                      <button 
                        className="btn btn-sm" 
                        onClick={() => handleMarkPaid(p.payment_id)}
                        style={{
                          background: 'linear-gradient(135deg, #00cc66, #009944)',
                          color: 'white',
                          border: 'none',
                          padding: '5px 15px',
                          borderRadius: '20px'
                        }}
                      >
                        <i className="fas fa-check me-1"></i>Mark Paid
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* RECORD PAYMENT FORM - Fixed styling */}
      {showForm && (
        <div className="card mb-4 shadow-sm" style={{ background: 'rgba(15, 20, 35, 0.9)', backdropFilter: 'blur(10px)' }}>
          <div className="card-header" style={{ background: '#1a1a2e', color: '#00ffff', fontFamily: 'Orbitron, monospace' }}>
            <i className="fas fa-credit-card me-2"></i>Record New Payment
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="row">
                <div className="col-md-3 mb-3">
                  <label className="form-label" style={{ color: '#00ffff' }}>Member ID</label>
                  <input type="number" className="form-control" name="member_id" value={formData.member_id} onChange={handleChange} required 
                    style={{ background: 'rgba(0,0,0,0.6)', color: 'white', border: '1px solid rgba(0,255,255,0.3)' }} />
                </div>
                <div className="col-md-3 mb-3">
                  <label className="form-label" style={{ color: '#00ffff' }}>Amount (Rs.)</label>
                  <input type="number" step="0.01" className="form-control" name="amount" value={formData.amount} onChange={handleChange} required 
                    style={{ background: 'rgba(0,0,0,0.6)', color: 'white', border: '1px solid rgba(0,255,255,0.3)' }} />
                </div>
                <div className="col-md-3 mb-3">
                  <label className="form-label" style={{ color: '#00ffff' }}>Method</label>
                  <select className="form-select" name="payment_method" value={formData.payment_method} onChange={handleChange}
                    style={{ background: 'rgba(0,0,0,0.6)', color: 'white', border: '1px solid rgba(0,255,255,0.3)' }}>
                    <option value="Cash">Cash</option>
                    <option value="Bank Transfer">Bank Transfer</option>
                    <option value="Card">Card</option>
                  </select>
                </div>
                <div className="col-md-3 mb-3">
                  <label className="form-label" style={{ color: '#00ffff' }}>Status</label>
                  <select className="form-select" name="status" value={formData.status} onChange={handleChange}
                    style={{ background: 'rgba(0,0,0,0.6)', color: 'white', border: '1px solid rgba(0,255,255,0.3)' }}>
                    <option value="paid">Paid</option>
                    <option value="pending">Pending</option>
                  </select>
                </div>
              </div>
              <button type="submit" className="btn btn-success mt-2">
                <i className="fas fa-save me-2"></i>Submit Payment
              </button>
            </form>
          </div>
        </div>
      )}

      {/* FULL PAYMENT HISTORY TABLE - Fixed styling */}
      <h4 style={{ color: '#00ffff', marginTop: '30px', marginBottom: '20px' }}>
        <i className="fas fa-history me-2"></i>Payment History
      </h4>
      <div className="table-responsive">
        <table className="table table-striped table-hover shadow-sm" style={{ background: 'rgba(10, 15, 30, 0.8)' }}>
          <thead style={{ background: 'linear-gradient(135deg, #0a0a1a, #12122a)' }}>
            <tr>
              <th style={{ color: '#00ffff', padding: '12px' }}>ID</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Member</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Amount</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Date</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Method</th>
              <th style={{ color: '#00ffff', padding: '12px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {payments.map(p => (
              <tr key={p.payment_id}>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>{p.payment_id}</td>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>{p.member}</td>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>Rs. {p.amount}</td>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>{new Date(p.payment_date).toLocaleDateString()}</td>
                <td style={{ color: '#e0e0e0', padding: '10px' }}>{p.payment_method}</td>
                <td style={{ padding: '10px' }}>
                  <span className={`badge`} style={{
                    background: p.status === 'paid' ? 'linear-gradient(135deg, #00cc66, #009944)' : 
                                p.status === 'pending' ? 'linear-gradient(135deg, #ffaa00, #ff7700)' : 
                                'linear-gradient(135deg, #ff3300, #cc2200)',
                    color: p.status === 'pending' ? '#1a1a1a' : 'white',
                    padding: '5px 12px',
                    borderRadius: '20px'
                  }}>
                    {p.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Payments;