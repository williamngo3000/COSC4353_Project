import React, { useState, useEffect } from 'react';
import EventList from './pages/EventList.jsx';
import VolunteerMatching from './pages/VolunteerMatching.jsx';
import VolunteerSelfMatch from './pages/VolunteerSelfMatch.jsx';

// --- Styles ---
const AppStyles = () => (
  <style>{`
    body, html, #root {
      margin: 0; padding: 0; height: 100%;
      font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
      background-color: #f9fafb;
      color: #1f2937;
    }
    .app-container {
      display: flex; flex-direction: column; align-items: center; min-height: 100vh;
    }
    .main-content { width: 100%; max-width: 1280px; padding: 2rem 1rem; box-sizing: border-box; }

    /* Navbar */
    .navbar { background-color: #fff; width: 100%; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); }
    .nav-container { display: flex; align-items: center; justify-content: space-between; height: 4rem; max-width: 1280px; margin: auto; padding: 0 1rem; }
    .nav-brand { font-size: 1.25rem; font-weight: bold; color: #b91c1c; background: none; border: none; cursor: pointer; }
    .nav-links { display: flex; align-items: center; gap: 1rem; }
    .nav-button, .nav-button-primary, .nav-button-secondary {
      padding: 0.5rem 0.75rem; font-size: 0.875rem; font-weight: 500; border: none; cursor: pointer; border-radius: 0.375rem;
    }
    .nav-button { color: #4b5563; background: none; transition: color 0.2s; }
    .nav-button:hover { color: #b91c1c; }
    .nav-button-primary { background-color: #b91c1c; color: white; border-radius: 9999px; padding: 0.5rem 1rem; }
    .nav-button-primary:hover { background-color: #991b1b; }
    .nav-button-secondary { background-color: #fee2e2; color: #991b1b; border-radius: 9999px; padding: 0.5rem 1rem; }
    .nav-button-secondary:hover { background-color: #fecaca; }

    /* Notification */
    .notification-container { position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 50; }
    .notification-popup { display: flex; align-items: center; padding: 1rem 1.5rem; border-radius: 0.5rem; color: white; min-width: 300px; box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1); }
    .notification-popup.success { background-color: #16a34a; }
    .notification-popup.error { background-color: #dc2626; }
    .notification-message { flex-grow: 1; }
    .notification-close { background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; margin-left: 1rem; }

    @media (min-width: 640px) { .main-content { padding: 2rem; } }
  `}</style>
);

// --- Notification Component ---
const Notification = ({ message, type, onClose }) => {
  if (!message) return null;
  useEffect(() => {
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [message, onClose]);

  return (
    <div className="notification-container">
      <div className={`notification-popup ${type}`}>
        <p className="notification-message">{message}</p>
        <button onClick={onClose} className="notification-close">&times;</button>
      </div>
    </div>
  );
};

// --- Simple Homepage ---
const HomePage = () => (
  <div style={{ textAlign: 'center', marginTop: '5rem' }}>
    <h1 style={{ fontSize: '3rem', fontWeight: 'bold', color: '#1f2937' }}>
      Event Management Hub
    </h1>
    <p style={{ fontSize: '1.25rem', color: '#6b7280', marginTop: '1rem' }}>
      Connecting volunteers with opportunities.
    </p>
  </div>
);

// --- App Component ---
export default function App() {
  const [page, setPage] = useState('home');
  const [loggedInUser, setLoggedInUser] = useState(null);
  const [notification, setNotification] = useState(null);

  const handleLogout = () => {
    setLoggedInUser(null);
    setPage('home');
  };

  const renderPage = () => {
    switch (page) {
      case 'eventList':
        if (!loggedInUser) return setPage('login');
        return <EventList />;
      case 'volunteerMatching':
        if (!loggedInUser || loggedInUser.role !== 'admin') {
          setNotification({ message: 'You must be an admin to view this page.', type: 'error' });
          setPage('home');
          return null;
        }
        return <VolunteerMatchingPage setNotification={setNotification} />;
      case 'volunteerSelfMatch':
        if (!loggedInUser) return setPage('login');
        return (
          <VolunteerSelfMatch
            loggedInUser={loggedInUser}
            setNotification={setNotification}
          />
        );
      case 'home':
      default:
        return <HomePage />;
    }
  };

  return (
    <div className="app-container">
      <AppStyles />
      <Notification
        message={notification?.message}
        type={notification?.type}
        onClose={() => setNotification(null)}
      />

      {/* Navbar */}
      <nav className="navbar">
        <div className="nav-container">
          <div>
            <button onClick={() => setPage('home')} className="nav-brand">
              EventApp
            </button>
          </div>

          <div className="nav-links">
            <button onClick={() => setPage('home')} className="nav-button">
              Home
            </button>

            {/* Volunteer self-match */}
            <button
              onClick={() => setPage('volunteerSelfMatch')}
              className="nav-button"
            >
              Find Matching Events
            </button>

            {loggedInUser ? (
              <>
                <button
                  onClick={() => setPage('eventList')}
                  className="nav-button"
                >
                  Event List
                </button>

                {loggedInUser.role === 'admin' ? (
                  <>
                    <button
                      onClick={() => setPage('eventManagement')}
                      className="nav-button"
                    >
                      Event Management
                    </button>
                    <button
                      onClick={() => setPage('volunteerMatching')}
                      className="nav-button"
                    >
                      Volunteer Matching
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setPage('profile')}
                    className="nav-button"
                  >
                    Profile
                  </button>
                )}

                <button
                  onClick={handleLogout}
                  className="nav-button-secondary"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setPage('login')}
                  className="nav-button"
                >
                  Login
                </button>
                <button
                  onClick={() => setPage('register')}
                  className="nav-button-primary"
                >
                  Register
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      <main className="main-content">{renderPage()}</main>
    </div>
  );
}

