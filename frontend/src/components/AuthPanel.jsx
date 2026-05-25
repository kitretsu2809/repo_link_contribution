import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function AuthPanel({ authMsg, setAuthMsg }) {
  const { user, login, register, logout } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handle = async (fn, label) => {
    setAuthMsg({ text: '', type: '' });
    try {
      await fn(email, password);
      setEmail(''); setPassword('');
      setAuthMsg({ text: `${label} successful.`, type: 'success' });
    } catch (e) {
      setAuthMsg({ text: e.message, type: 'error' });
    }
  };

  return (
    <div className={`auth-panel ${user ? 'logged-in' : ''}`}>
      {!user ? (
        <div className="auth-guest">
          <div className="auth-status">Signed in as <strong>guest</strong>. Login to star repositories and receive issue emails.</div>
          <input className="auth-input" type="email" placeholder="Email address" value={email} onChange={e => setEmail(e.target.value)} />
          <input className="auth-input" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handle(login, 'Login')} />
          <button className="btn btn-sm" onClick={() => handle(login, 'Login')}>Login</button>
          <button className="btn btn-sm btn-outline" onClick={() => handle(register, 'Register')}>Register</button>
        </div>
      ) : (
        <div className="auth-user" style={{ display: 'flex', width: '100%', justifyContent: 'space-between', alignItems: 'center' }}>
          <div className="profile-chip">
            <span className="profile-icon">◉</span>
            <div className="profile-copy">
              <span className="profile-email">{user.email}</span>
              <span className="profile-note">Email notifications are active for starred repositories</span>
            </div>
          </div>
          <button className="btn btn-sm btn-outline" onClick={async () => { await logout(); setAuthMsg({ text: 'Logged out.', type: 'success' }); }}>Logout</button>
        </div>
      )}
      {authMsg?.text && (
        <div className={`auth-message ${authMsg.type}`}>{authMsg.text}</div>
      )}
    </div>
  );
}
