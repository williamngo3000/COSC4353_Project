import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
// import { ColorModeContext, useMode, tokens } from './theme';
import { ColorModeContext, useMode } from './theme';
import { CssBaseline, ThemeProvider } from "@mui/material";
import Topbar from "./scenes/global/Topbar";
import Sidebar from "./scenes/global/Sidebar";
import Navbar from './scenes/global/Navbar';
import HomePage from './scenes/home';
import LoginPage from './scenes/login';
import RegisterPage from './scenes/register';
import ProfilePage from './scenes/profile';
import EventManagementPage from './scenes/eventManagement';
import EventList from './scenes/eventList';
import Dashboard from "./scenes/dashboard";
import Users from "./scenes/users";
import Events from "./scenes/events";
import Form from "./scenes/form";
import VolunteerNotifications from "./scenes/notifications/VolunteerNotifications";
import AdminNotifications from "./scenes/notifications/AdminNotifications";
import NotificationQueue from './components/Notification';
import './styles/app.css';

export default function App() {
    const [theme, colorMode] = useMode();
    const [isSidebar, setIsSidebar] = useState(true);
    const [loggedInUser, setLoggedInUser] = useState(null);
    const [notifications, setNotifications] = useState([]);

    const handleLogout = () => {
        setLoggedInUser(null);
    };

    // Notification queue management
    const addNotification = (message, type = 'info') => {
        const id = Date.now();
        setNotifications(prev => [...prev, { id, message, type }]);
    };

    const removeNotification = (id) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    };

    const isAdmin = loggedInUser?.role === 'admin';

    // Inject theme color as CSS variable for .app background (main focus is admin dashboard bc light/dark mode)
    useEffect(() => {
        // const colors = tokens(theme.palette.mode);
        // document.documentElement.style.setProperty('--app-bg-color', colors.primary[500]);
        document.documentElement.style.setProperty('--app-bg-color', theme.palette.background.default);
    }, [theme.palette.mode]);

    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <Router>
                    <div className={isAdmin ? "app" : "app-container"}>
                        <NotificationQueue
                            notifications={notifications}
                            onClose={removeNotification}
                        />
                        {isAdmin && <Sidebar isSidebar={isSidebar} />}
                        <main className={isAdmin ? "content" : "main-content"}>
                            {isAdmin && <Topbar setIsSidebar={setIsSidebar} onLogout={handleLogout} />}
                            {!isAdmin && <Navbar loggedInUser={loggedInUser} handleLogout={handleLogout} />}
                            <Routes>
                                <Route
                                    path="/"
                                    element={
                                        isAdmin ? <Navigate to="/dashboard" replace /> :
                                        loggedInUser ? <Navigate to="/eventlist" replace /> :
                                        <HomePage />
                                    }
                                />
                                <Route
                                    path="/login"
                                    element={
                                        <LoginPage
                                            setLoggedInUser={setLoggedInUser}
                                            addNotification={addNotification}
                                        />
                                    }
                                />
                                <Route
                                    path="/register"
                                    element={<RegisterPage setLoggedInUser={setLoggedInUser} addNotification={addNotification} />}
                                />
                                <Route
                                    path="/dashboard"
                                    element={
                                        isAdmin ? (
                                            <Dashboard addNotification={addNotification} />
                                        ) : (
                                            <Navigate to="/login" replace />
                                        )
                                    }
                                />
                                <Route
                                    path="/users"
                                    element={
                                        isAdmin ? (
                                            <Users addNotification={addNotification} />
                                        ) : (
                                            <Navigate to="/login" replace />
                                        )
                                    }
                                />
                                <Route
                                    path="/events"
                                    element={
                                        isAdmin ? (
                                            <Events addNotification={addNotification} />
                                        ) : (
                                            <Navigate to="/login" replace />
                                        )
                                    }
                                />
                                <Route
                                    path="/form"
                                    element={
                                        isAdmin ? (
                                            <Form addNotification={addNotification} />
                                        ) : (
                                            <Navigate to="/login" replace />
                                        )
                                    }
                                />
                                <Route
                                    path="/profile"
                                    element={
                                        loggedInUser ? (
                                            <ProfilePage
                                                loggedInUser={loggedInUser}
                                                setLoggedInUser={setLoggedInUser}
                                                addNotification={addNotification}
                                            />
                                        ) : (
                                            <Navigate to="/login" replace />
                                        )
                                    }
                                />
                                <Route
                                    path="/Dashboard"
                                    element={
                                        isAdmin ? (
                                            <Dashboard addNotification={addNotification} />
                                        ) : (
                                            <Navigate to="/login" replace />
                                        )
                                    }
                                />
                                <Route
                                    path="/eventlist"
                                    element={
                                        loggedInUser ? (
                                            <EventList addNotification={addNotification} />
                                        ) : (
                                            <Navigate to="/login" replace />
                                        )
                                    }
                                />
                                <Route
                                    path="/eventmanagement"
                                    element={
                                        loggedInUser ? (
                                            <EventManagementPage addNotification={addNotification} />
                                        ) : (
                                            <Navigate to="/login" replace />
                                        )
                                    }
                                />
                                <Route
                                    path="/notifications"
                                    element={
                                        isAdmin ? (
                                            <AdminNotifications addNotification={addNotification} />
                                        ) : loggedInUser ? (
                                            <VolunteerNotifications
                                                loggedInUser={loggedInUser}
                                                addNotification={addNotification}
                                            />
                                        ) : (
                                            <Navigate to="/login" replace />
                                        )
                                    }
                                />
                            </Routes>
                        </main>
                    </div>
                </Router>
            </ThemeProvider>
        </ColorModeContext.Provider>
    );
}