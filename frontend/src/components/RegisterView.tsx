import { useState, type FormEvent } from 'react';
import { register } from '../services/api';
import './AuthView.css';

interface RegisterViewProps {
  onSuccess: () => void;
  onSwitchToLogin: () => void;
}

export default function RegisterView({ onSuccess, onSwitchToLogin }: RegisterViewProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await register(username, password);
      // Dopo la registrazione con successo, andiamo al login
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore durante la registrazione');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-view">
      <div className="auth-card">
        <div className="auth-header">
          <h2 className="auth-title">Nuovo Account</h2>
          <p className="auth-subtitle">Inizia a pianificare i tuoi viaggi con TripAI</p>
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
              placeholder="Scegli un username"
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
              placeholder="Crea una password"
            />
          </div>

          {error && <div className="auth-error">{error}</div>}

          <button className="auth-btn" type="submit" disabled={isLoading}>
            {isLoading ? 'Registrazione...' : 'Registrati'}
          </button>
        </form>

        <div className="auth-footer">
          Hai già un account?
          <button className="auth-link" onClick={onSwitchToLogin} disabled={isLoading}>
            Accedi qui
          </button>
        </div>
      </div>
    </div>
  );
}
