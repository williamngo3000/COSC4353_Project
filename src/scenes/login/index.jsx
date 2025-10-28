import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MailIcon, LockIcon } from '../../components/Icons';

const LoginPage = ({ setLoggedInUser, addNotification }) => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [err, setErr] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();
        setErr("");
        setLoading(true);
        const email = e.target.email.value;
        const password = e.target.password.value;

        try {
            const res = await fetch("http://localhost:5001/login", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({email, password})
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data?.message);
            }

            const user = data.user;
            setLoggedInUser(user);
            addNotification("Login successful!", "success");

            if (user.role === "admin") {
                navigate("/dashboard");
            } else if (user.profileComplete) {
                navigate("/eventlist");
            } else {
                navigate("/profile");
            }
        } catch (e) {
            setErr(e.message);
            addNotification(e.message || "Error: failed to log in", "error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-card">
            <div className="form-header">
                <h2>Welcome Back!</h2>
                <p>Log in to manage your events and profile.</p>
            </div>
            <form onSubmit={handleLogin} className="form-container">
                <div className="form-input-group">
                    <MailIcon className="form-input-icon" />
                    <input type="email" name="email" placeholder="Email (username)" required className="form-input" />
                </div>
                <div className="form-input-group">
                    <LockIcon className="form-input-icon" />
                    <input type="password" name="password" placeholder="Password" required className="form-input" />
                </div>
                <button type="submit" className="form-button">Login</button>
                <p className="form-footer-text">
                    Not registered yet?{' '}
                    <Link to="/register" className="form-footer-link">Register</Link>
                </p>
                <p style={{textAlign: 'center', fontSize: '0.75rem', color: '#a1a1aa', paddingTop: '0.5rem'}}>
                    Hint: Use <strong>admin@example.com</strong> to log in as an admin.
                </p>
            </form>
        </div>
    );
};

export default LoginPage;
