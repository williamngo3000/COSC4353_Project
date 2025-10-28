import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MailIcon, LockIcon } from '../../../components/Icons';

const RegisterPage = ({ setLoggedInUser, addNotification }) => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        const email = e.target.email.value;
        const password = e.target.password.value;
        const confirmPassword = e.target.confirmPassword.value;

        if (password !== confirmPassword) {
            addNotification('Passwords do not match. Please try again.', 'error');
            setLoading(false);
            return;
        }

        // PW validation: at least 8 chars, one number, one uppercase letter
        const hasNumber = /[0-9]/.test(password);
        const hasUppercase = /[A-Z]/.test(password);

        if (password.length < 8 || !hasNumber || !hasUppercase) {
            addNotification('Password must be at least 8 characters, and include a number and an uppercase letter.', 'error');
            setLoading(false);
            return;
        }

        try {
            const res = await fetch("http://localhost:5001/register", {
                method: "POST",
                headers: { "Content-Type": "application/json"},
                body: JSON.stringify({email, password}),
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data?.message);
            }

            setLoggedInUser(data.user);
            addNotification('Registration successful! Please complete your profile.', 'success');
            navigate('/profile');
        } catch (err) {
            addNotification(err.message || "Error: registration failed", "error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-card">
            <div className="form-header">
                <h2>Create Your Account</h2>
                <p>Join our community of volunteers and administrators.</p>
            </div>
            <form onSubmit={handleRegister} className="form-container">
                <div className="form-input-group">
                    <MailIcon className="form-input-icon" />
                    <input type="email" name="email" placeholder="Email (username)" required className="form-input" />
                </div>
                <div className="form-input-group">
                    <LockIcon className="form-input-icon" />
                    <input type="password" name="password" placeholder="Password" required className="form-input" />
                </div>
                <div className="form-input-group">
                    <LockIcon className="form-input-icon" />
                    <input type="password" name="confirmPassword" placeholder="Confirm Password" required className="form-input" />
                </div>
                <button type="submit" className="form-button">Register</button>
                <p className="form-footer-text">
                    Already have an account?{' '}
                    <Link to="/login" className="form-footer-link">Login</Link>
                </p>
            </form>
        </div>
    );
};

export default RegisterPage;
