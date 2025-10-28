import { Link, useNavigate } from 'react-router-dom';

const Navbar = ({ loggedInUser, handleLogout }) => {
    const navigate = useNavigate();

    const onLogout = () => {
        handleLogout();
        navigate('/');
    };

    return (
        <nav className="navbar">
            <div className="nav-container">
                <div>
                    <Link to="/" className="nav-brand">
                        EventApp
                    </Link>
                </div>
                <div className="nav-links">
                    <Link to="/" className="nav-button">Home</Link>

                    {loggedInUser ? (
                        <>
                            <Link to="/eventlist" className="nav-button">EventList</Link>
                            {loggedInUser.role === 'admin' ? (
                                <Link to="/eventmanagement" className="nav-button">Event Management</Link>
                            ) : (
                                <Link to="/profile" className="nav-button">Profile</Link>
                            )}
                            <Link to="/notifications" className="nav-button">Notifications</Link>
                            <button onClick={onLogout} className="nav-button-secondary">Logout</button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="nav-button">Login</Link>
                            <Link to="/register" className="nav-button-primary">Register</Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
