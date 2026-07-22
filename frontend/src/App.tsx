import { useState, useEffect } from 'react';
import ChatView from './components/ChatView';
import DashboardView from './components/DashboardView';
import LoginView from './components/LoginView';
import RegisterView from './components/RegisterView';
import { getToken, removeToken, getLoggedUsername } from './services/api';
import type { Booking } from './types';
import './App.css';

type ActiveView = 'chat' | 'dashboard';

export default function App() {
  const [activeView, setActiveView] = useState<ActiveView>('chat');
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [modifyBooking, setModifyBooking] = useState<Booking | null>(null);

  useEffect(() => {
    if (getToken()) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogout = () => {
    removeToken();
    setIsAuthenticated(false);
    setAuthView('login');
  };

  if (!isAuthenticated) {
    if (authView === 'login') {
      return (
        <LoginView
          onSuccess={() => setIsAuthenticated(true)}
          onSwitchToRegister={() => setAuthView('register')}
        />
      );
    }
    return (
      <RegisterView
        onSuccess={() => setAuthView('login')}
        onSwitchToLogin={() => setAuthView('login')}
      />
    );
  }

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__brand">
          <div className="app__compass">
            <span className="app__compass-icon">✦</span>
          </div>
          <h1 className="app__title">TripAI</h1>
        </div>

        <nav className="app__nav">
          <button
            className={`app__nav-btn ${activeView === 'chat' ? 'app__nav-btn--active' : ''}`}
            onClick={() => setActiveView('chat')}
          >
            💬 Chat
          </button>
          <button
            className={`app__nav-btn ${activeView === 'dashboard' ? 'app__nav-btn--active' : ''}`}
            onClick={() => setActiveView('dashboard')}
          >
            📋 I miei viaggi
          </button>
        </nav>

        <div className="app__user-actions">
          <span className="app__user-greeting">
            👋 Ciao, {getLoggedUsername()}!
          </span>
          <button className="app__nav-btn" onClick={handleLogout}>
            🚪 Logout
          </button>
        </div>
      </header>

      <main className="app__content">
        {activeView === 'chat' ? (
          <ChatView modifyBooking={modifyBooking} onModifyHandled={() => setModifyBooking(null)} />
        ) : (
          <DashboardView onModifyBooking={(b) => {
            setModifyBooking(b);
            setActiveView('chat');
          }} />
        )}
      </main>
    </div>
  );
}
