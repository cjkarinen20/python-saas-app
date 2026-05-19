import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Auth.css';

const Signup: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    // ==== TODO: BACKEND API INTEGRATION - User Registration ====
    // This calls the signup function from AuthContext
    // You need to implement the signup API call in AuthContext.tsx
    // See AuthContext.tsx for implementation details
    const success = await signup(email, password);

    if (success) {
      navigate('/login', {
        state: { message: 'Account created successfully! Please log in.' }
      });
    } else {
      setError('Failed to create account. Email may already exist.');
    }
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-background"></div>
      <div className="auth-form-container">
        <h1>Story Generation SaaS</h1>
        <form onSubmit={handleSubmit} className="auth-form">
          <h2>Sign Up</h2>
          {error && <div className="error-message">{error}</div>}
          <div className="form-group">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" disabled={loading} className="auth-button">
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>
          <p>
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Signup;