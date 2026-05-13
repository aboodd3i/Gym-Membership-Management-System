import { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { loginUser } from '../api/gymApi';

function Login() {
  const { login } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); // Clear previous errors

    try {
      const response = await loginUser({ email, password });
      // If successful, save user data to context/localStorage
      login(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password.');
    }
  };

  return (
    <div className="d-flex align-items-center justify-content-center" style={{ minHeight: '80vh' }}>
      <div className="card shadow-lg border-0" style={{ 
        width: '400px', 
        borderRadius: '16px',
        background: 'rgba(15, 20, 35, 0.95)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(0, 255, 255, 0.2)'
      }}>
        <div className="card-body p-5">
          <div className="text-center mb-4">
            <i className="fas fa-bolt fa-3x mb-3" style={{ color: '#ff7700' }}></i>
            <h3 className="fw-bold" style={{ 
              background: 'linear-gradient(135deg, #ff2e00, #ff7700, #ffcc00)',
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text',
              color: 'transparent'
            }}>FAST GYM</h3>
            <p style={{ color: '#aaaacc' }}>Sign in to your account</p>
          </div>

          {error && (
            <div className="alert text-center" role="alert" style={{ 
              borderRadius: '12px',
              background: 'linear-gradient(135deg, rgba(255, 51, 0, 0.25), rgba(204, 34, 0, 0.25))',
              border: '1px solid #ff3300',
              color: '#ffaa88',
              padding: '12px 20px',
              fontSize: '0.9rem',
              fontWeight: '500',
              boxShadow: '0 0 15px rgba(255, 51, 0, 0.3)'
            }}>
              <i className="fas fa-exclamation-triangle me-2" style={{ color: '#ff6600' }}></i>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label fw-bold" style={{ color: '#00ffff' }}>Email address</label>
              <div className="input-group">
                <span className="input-group-text" style={{ 
                  background: 'rgba(0, 0, 0, 0.6)', 
                  border: '1px solid rgba(0, 255, 255, 0.3)',
                  color: '#00ffff'
                }}>
                  <i className="fas fa-envelope"></i>
                </span>
                <input 
                  type="email" 
                  className="form-control" 
                  placeholder="Enter Admin Email"
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                  required 
                  style={{
                    background: 'rgba(0, 0, 0, 0.6)',
                    border: '1px solid rgba(0, 255, 255, 0.3)',
                    color: 'white'
                  }}
                />
              </div>
            </div>
            
            <div className="mb-4">
              <label className="form-label fw-bold" style={{ color: '#00ffff' }}>Password</label>
              <div className="input-group">
                <span className="input-group-text" style={{ 
                  background: 'rgba(0, 0, 0, 0.6)', 
                  border: '1px solid rgba(0, 255, 255, 0.3)',
                  color: '#00ffff'
                }}>
                  <i className="fas fa-lock"></i>
                </span>
                <input 
                  type="password" 
                  className="form-control" 
                  placeholder="Enter Admin Password"
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  required 
                  style={{
                    background: 'rgba(0, 0, 0, 0.6)',
                    border: '1px solid rgba(0, 255, 255, 0.3)',
                    color: 'white'
                  }}
                />
              </div>
            </div>

            <button type="submit" className="btn w-100 py-2 fw-bold" style={{ 
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #ff2e00, #ff7700)',
              border: 'none',
              color: 'white',
              transition: 'all 0.3s ease'
            }}>
              Sign In <i className="fas fa-arrow-right ms-2"></i>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Login;