import { useState, type FormEvent } from 'react';
import { login, setToken } from '../services/api';
import './AuthView.css';

interface LoginViewProps {
  onSuccess: () => void;
  onSwitchToRegister: () => void;
}

export default function LoginView({ onSuccess, onSwitchToRegister }: LoginViewProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const data = await login(username, password);
      setToken(data.access_token);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore durante il login');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-view">
      <div className="auth-card">
        <div className="auth-header">
          <h2 className="auth-title">Bentornato!</h2>
          <p className="auth-subtitle">Accedi a TripAI</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-input-group">
            <label className="auth-label" htmlFor="username">Username</label>
            <input
              className="auth-input"
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={isLoading}
              placeholder="Inserisci il tuo username"
            />
          </div>

          <div className="auth-input-group">
            <label className="auth-label" htmlFor="password">Password</label>
            <input
              className="auth-input"
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
              placeholder="••••••••"
            />
          </div>

          {error && <div className="auth-error">{error}</div>}

          <button className="auth-btn" type="submit" disabled={isLoading}>
            {isLoading ? 'Accesso in corso...' : 'Accedi'}
          </button>
        </form>

        <div className="auth-footer">
          Non hai ancora un account?
          <button className="auth-link" onClick={onSwitchToRegister} disabled={isLoading}>
            Registrati qui
          </button>
        </div>
      </div>
    </div>
  );
}
