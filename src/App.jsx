import React, { useState, useEffect } from 'react';
import EventList from './pages/EventList.jsx';



// first draft of the frontend 
// this is to fix centering issues with webpage
const AppStyles = () => (
    <style>{`
        /* --- Base & Layout --- */
        body, html, #root {
          margin: 0;
          padding: 0;
          height: 100%;
          font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
          background-color: #f9fafb; /* bg-gray-50 */
          color: #1f2937; /* text-gray-800 */
        }

        .app-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          min-height: 100vh;
        }

        .main-content {
            width: 100%;
            max-width: 1280px; /* max-w-7xl */
            padding: 2rem 1rem;
            box-sizing: border-box;
        }

        /* --- Navigation Bar --- */
        .navbar {
            background-color: #ffffff;
            width: 100%;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }
        .nav-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 4rem; /* h-16 */
            max-width: 1280px;
            margin: auto;
            padding: 0 1rem;
        }
        .nav-brand {
            font-size: 1.25rem;
            font-weight: bold;
            color: #b91c1c; /* text-red-700 */
            background: none;
            border: none;
            cursor: pointer;
        }
        .nav-links {
            display: flex;
            align-items: center;
            gap: 1rem; /* space-x-4 */
        }
        .nav-button {
            color: #4b5563; /* text-gray-600 */
            padding: 0.5rem 0.75rem;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            font-weight: 500;
            background: none;
            border: none;
            cursor: pointer;
            transition: color 0.2s;
        }
        .nav-button:hover {
            color: #b91c1c; /* hover:text-red-700 */
        }
        .nav-button-primary {
            background-color: #b91c1c; /* bg-red-700 */
            color: #ffffff;
            padding: 0.5rem 1rem;
            border-radius: 9999px; /* rounded-full */
            font-size: 0.875rem;
            font-weight: 500;
            border: none;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .nav-button-primary:hover {
            background-color: #991b1b; /* hover:bg-red-800 */
        }
        .nav-button-secondary {
            background-color: #fee2e2; /* bg-red-100 */
            color: #991b1b; /* text-red-800 */
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
            border: none;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .nav-button-secondary:hover {
            background-color: #fecaca; /* hover:bg-red-200 */
        }

        /* --- Login/Register Forms --- */
        .form-card {
            max-width: 28rem;
            margin: 2.5rem auto 0 auto;
        }
        .form-container {
             background-color: #ffffff;
             padding: 2rem;
             border-radius: 0.5rem;
             box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        }
        .form-header { text-align: center; margin-bottom: 2rem; }
        .form-header h2 { font-size: 1.875rem; font-weight: bold; color: #1f2937; }
        .form-header p { color: #6b7280; }
        .form-input-group { position: relative; margin-bottom: 1.5rem; }
        .form-input {
            width: 100%;
            padding: 0.5rem 1rem 0.5rem 2.5rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            box-sizing: border-box;
        }
        .form-input:focus { outline: none; box-shadow: 0 0 0 2px #ef4444; }
        .form-input-icon { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); color: #9ca3af; width: 1.25rem; height: 1.25rem; }
        .form-button { width: 100%; padding: 0.5rem; border: none; border-radius: 0.5rem; background-color: #b91c1c; color: white; cursor: pointer; transition: background-color 0.3s; }
        .form-button:hover { background-color: #991b1b; }
        .form-footer-text { text-align: center; font-size: 0.875rem; color: #374151; margin-top: 1rem; }
        .form-footer-link { font-weight: 500; color: #b91c1c; background: none; border: none; cursor: pointer; }
        .form-footer-link:hover { text-decoration: underline; }

        /* --- Profile/Event Cards & Forms --- */
        .content-card {
            max-width: 56rem;
            margin: 2.5rem auto 0 auto;
            padding: 2rem;
            background-color: #ffffff;
            border-radius: 0.5rem;
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        }
        .content-card h2 { font-size: 1.875rem; font-weight: bold; color: #1f2937; margin-bottom: 0.5rem; }
        .content-card p { color: #6b7280; margin-bottom: 2rem; }
        .form-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
        @media (min-width: 768px) {
            .form-grid { grid-template-columns: repeat(2, 1fr); }
            .form-grid-col-span-2 { grid-column: span 2 / span 2; }
            .form-grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
        }
        .form-label { display: block; font-size: 0.875rem; font-weight: 500; color: #4b5563; margin-bottom: 0.25rem; }
        .form-input-full, .form-select, .form-textarea {
            width: 100%;
            padding: 0.5rem 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            box-sizing: border-box;
            background-color: white;
            font-size: 1rem;
        }
        .form-input-full:focus, .form-select:focus, .form-textarea:focus { outline: none; box-shadow: 0 0 0 2px #ef4444; }
        .form-textarea { resize: vertical; }
        .form-actions { text-align: right; }
        .button-submit { background-color: #b91c1c; color: white; padding: 0.5rem 1.5rem; border-radius: 0.5rem; border: none; cursor: pointer; transition: background-color 0.2s; }
        .button-submit:hover { background-color: #991b1b; }
        
        /* --- Availability Section --- */
        .availability-controls { display: flex; align-items: center; gap: 0.5rem; }
        .availability-input { flex-grow: 1; }
        .button-add { background-color: #e5e7eb; color: #374151; padding: 0.5rem 1rem; border-radius: 0.5rem; border: none; cursor: pointer; transition: background-color 0.2s; }
        .button-add:hover { background-color: #d1d5db; }
        .availability-tags { margin-top: 0.75rem; display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .availability-tag { background-color: #fee2e2; color: #991b1b; font-size: 0.875rem; font-weight: 500; padding: 0.25rem 0.75rem; border-radius: 9999px; display: flex; align-items: center; gap: 0.5rem; }
        .availability-tag button { background: none; border: none; cursor: pointer; line-height: 1; }
        .availability-tag-icon { width: 1rem; height: 1rem; }
        .availability-tag-icon:hover { color: #b91c1c; }
        
        /* --- Custom Multi-Select --- */
        .multiselect-container { position: relative; }
        .multiselect-button { width: 100%; box-sizing: border-box; background-color: white; border: 1px solid #d1d5db; border-radius: 0.5rem; box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); padding: 0.5rem 2.5rem 0.5rem 0.75rem; text-align: left; cursor: default; }
        .multiselect-button:focus { outline: none; box-shadow: 0 0 0 2px #ef4444; border-color: #ef4444; }
        .multiselect-placeholder { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .multiselect-chevron { position: absolute; right: 0.5rem; top: 50%; transform: translateY(-50%); pointer-events: none; color: #9ca3af; width: 1.25rem; height: 1.25rem; }
        .multiselect-dropdown { position: absolute; margin-top: 0.25rem; width: 100%; border-radius: 0.375rem; background-color: white; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); z-index: 10; }
        .multiselect-list { list-style: none; margin: 0; padding: 0.25rem 0; max-height: 15rem; border-radius: 0.375rem; border: 1px solid rgba(0,0,0,0.05); overflow: auto; }
        .multiselect-item { color: #111827; cursor: default; user-select: none; position: relative; padding: 0.5rem 2.25rem 0.5rem 0.75rem; }
        .multiselect-item:hover { background-color: #fee2e2; }
        .multiselect-item-text-selected { font-weight: 600; }
        .multiselect-item-check { color: #dc2626; position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); }

        /* --- Notification Popup --- */
        .notification-container {
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            z-index: 50;
        }
        .notification-popup {
            display: flex;
            align-items: center;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            color: white;
            min-width: 300px;
        }
        .notification-popup.success {
            background-color: #16a34a; /* green-600 */
        }
        .notification-popup.error {
            background-color: #dc2626; /* red-600 */
        }
        .notification-message {
            flex-grow: 1;
        }
        .notification-close {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            line-height: 1;
            cursor: pointer;
            margin-left: 1rem;
        }


        /* Responsive */
        @media (min-width: 640px) {
            .main-content { padding-left: 1.5rem; padding-right: 1.5rem; }
            .nav-container { padding: 0 1.5rem; }
        }
        @media (min-width: 1024px) {
            .main-content { padding-left: 2rem; padding-right: 2rem; }
            .nav-container { padding: 0 2rem; }
        }
    `}</style>
);



const US_STATES = [
    { code: 'AL', name: 'Alabama' }, { code: 'AK', name: 'Alaska' }, { code: 'AZ', name: 'Arizona' },
    { code: 'AR', name: 'Arkansas' }, { code: 'CA', name: 'California' }, { code: 'CO', name: 'Colorado' },
    { code: 'CT', name: 'Connecticut' }, { code: 'DE', name: 'Delaware' }, { code: 'FL', name: 'Florida' },
    { code: 'GA', name: 'Georgia' }, { code: 'HI', name: 'Hawaii' }, { code: 'ID', name: 'Idaho' },
    { code: 'IL', name: 'Illinois' }, { code: 'IN', name: 'Indiana' }, { code: 'IA', name: 'Iowa' },
    { code: 'KS', name: 'Kansas' }, { code: 'KY', name: 'Kentucky' }, { code: 'LA', name: 'Louisiana' },
    { code: 'ME', name: 'Maine' }, { code: 'MD', name: 'Maryland' }, { code: 'MA', name: 'Massachusetts' },
    { code: 'MI', name: 'Michigan' }, { code: 'MN', name: 'Minnesota' }, { code: 'MS', name: 'Mississippi' },
    { code: 'MO', name: 'Missouri' }, { code: 'MT', name: 'Montana' }, { code: 'NE', name: 'Nebraska' },
    { code: 'NV', name: 'Nevada' }, { code: 'NH', name: 'New Hampshire' }, { code: 'NJ', name: 'New Jersey' },
    { code: 'NM', name: 'New Mexico' }, { code: 'NY', name: 'New York' }, { code: 'NC', name: 'North Carolina' },
    { code: 'ND', name: 'North Dakota' }, { code: 'OH', name: 'Ohio' }, { code: 'OK', name: 'Oklahoma' },
    { code: 'OR', name: 'Oregon' }, { code: 'PA', name: 'Pennsylvania' }, { code: 'RI', name: 'Rhode Island' },
    { code: 'SC', name: 'South Carolina' }, { code: 'SD', name: 'South Dakota' }, { code: 'TN', name: 'Tennessee' },
    { code: 'TX', name: 'Texas' }, { code: 'UT', name: 'Utah' }, { code: 'VT', name: 'Vermont' },
    { code: 'VA', name: 'Virginia' }, { code: 'WA', name: 'Washington' }, { code: 'WV', name: 'West Virginia' },
    { code: 'WI', name: 'Wisconsin' }, { code: 'WY', name: 'Wyoming' }
];

const SKILLS_LIST = ['First Aid', 'Logistics', 'Event Setup', 'Public Speaking', 'Registration', 'Tech Support', 'Catering', 'Marketing', 'Fundraising', 'Photography', 'Social Media', 'Team Leadership', 'Translation'];
const URGENCY_LEVELS = ['Low', 'Medium', 'High', 'Critical'];


const ChevronDownIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="m6 9 6 6 6-6" /></svg>
);
const MailIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><rect width="20" height="16" x="2" y="4" rx="2" /><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" /></svg>
);
const LockIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><rect width="18" height="11" x="3" y="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></svg>
);
const CheckIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M20 6 9 17l-5-5" /></svg>
);
const XIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M18 6 6 18" /><path d="m6 6 12 12" /></svg>
);


// --- Helper Components ---
const Notification = ({ message, type, onClose }) => {
    if (!message) return null;

    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, 5000); // Auto-dismiss after 5 seconds

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

const CustomMultiSelect = ({ options, selected, onChange, placeholder }) => {
    const [isOpen, setIsOpen] = useState(false);

    const toggleOption = (option) => {
        const newSelected = selected.includes(option)
            ? selected.filter(item => item !== option)
            : [...selected, option];
        onChange(newSelected);
    };

    return (
        <div className="multiselect-container">
            <button
                type="button"
                className="multiselect-button"
                onClick={() => setIsOpen(!isOpen)}
            >
                <span className="multiselect-placeholder">
                    {selected.length > 0 ? selected.join(', ') : placeholder}
                </span>
                <span className="multiselect-chevron">
                    <ChevronDownIcon />
                </span>
            </button>
            {isOpen && (
                <div className="multiselect-dropdown">
                    <ul className="multiselect-list">
                        {options.map(option => (
                            <li
                                key={option}
                                className="multiselect-item"
                                onClick={() => toggleOption(option)}
                            >
                                <span className={selected.includes(option) ? 'multiselect-item-text-selected' : ''}>
                                    {option}
                                </span>
                                {selected.includes(option) && (
                                    <span className="multiselect-item-check">
                                        <CheckIcon className="h-5 w-5" />
                                    </span>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

// Page Components

const LoginPage = ({ setPage, setLoggedInUser, setNotification }) => {
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
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();

            if (!res.ok) {
                //If invalid email or password
                throw new Error(data?.message);
            }

            const user = data.user;
            setLoggedInUser(user);
            setNotification({ message: "Login successful!", type: "success" });
            if (user.role === "admin") {
                setPage("eventManagement");
            } else if (user.profileComplete) {
                setPage("eventList");
            } else {
                setPage("profile");
            }



        } catch (e) {
            setErr(e.message);
            setNotification({ message: e.message || "Error: failed to log in", type: "error" });
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
                    <button type="button" onClick={() => setPage('register')} className="form-footer-link">Register</button>
                </p>
                <p style={{ textAlign: 'center', fontSize: '0.75rem', color: '#a1a1aa', paddingTop: '0.5rem' }}>
                    Hint: Use <strong>admin@example.com</strong> to log in as an admin.
                </p>
            </form>
        </div>
    );
};

const RegisterPage = ({ setPage, setLoggedInUser, setNotification }) => {

    const [loading, setLoading] = useState(false);

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        const email = e.target.email.value;
        const password = e.target.password.value;
        const confirmPassword = e.target.confirmPassword.value;

        if (password !== confirmPassword) {
            setNotification({ message: 'Passwords do not match. Please try again.', type: 'error' });
            setLoading(false);
            return;
        }

        // PW validation: at least 8 chars, one number, one uppercase letter
        const hasNumber = /[0-9]/.test(password);
        const hasUppercase = /[A-Z]/.test(password);

        if (password.length < 8 || !hasNumber || !hasUppercase) {
            setNotification({
                message: 'Password must be at least 8 characters, and include a number and an uppercase letter.',
                type: 'error'
            });
            setLoading(false);
            return;
        }
        // --- End of Validation ---

        try {
            const res = await fetch("http://localhost:5001/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),

            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data?.message);
            }

            setLoggedInUser(data.user);
            setNotification({ message: 'Registration successful! Please complete your profile.', type: 'success' });
            setPage('profile');

        } catch (err) {
            setNotification({ message: err.message || "Error: registration failed", type: "error" });
        } finally {
            setLoading(false);
        }

        //setLoggedInUser({ email: e.target.email.value, role: 'volunteer', profileComplete: false });


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
                    <button type="button" onClick={() => setPage('login')} className="form-footer-link">Login</button>
                </p>
            </form>
        </div>
    );
};

const ProfilePage = ({ setPage, loggedInUser, setLoggedInUser, setNotification }) => {

    const [loading, setLoading] = useState(true);

    //Usestates to change fields if they already have info
    const [fullName, setFullName] = useState("");
    const [address1, setAddress1] = useState("");
    const [address2, setAddress2] = useState("");
    const [city, setCity] = useState("");
    const [stateCode, setStateCode] = useState("");
    const [zip, setZip] = useState("");
    const [preferences, setPreferences] = useState("");
    const [skills, setSkills] = useState([]);
    const [availability, setAvailability] = useState([]);

    //Try and load up any data they might have
    useEffect(() => {
        if (!loggedInUser?.email) return;
        (async () => {
            try {
                const res = await fetch(`http://localhost:5001/profile/${encodeURIComponent(loggedInUser.email)}`);
                // If no profile yet
                if (!res.ok) throw new Error(`Failed to load profile (${res.status})`);
                const p = await res.json();

                setFullName(p.full_name || "");
                setAddress1(p.address1 || "");
                setAddress2(p.address2 || "");
                setCity(p.city || "");
                setStateCode(p.state || "");
                setZip(p.zip_code || "");
                setPreferences(p.preferences || "");
                setSkills(Array.isArray(p.skills) ? p.skills : []);
                setAvailability(Array.isArray(p.availability) ? p.availability : []);
            } catch (e) {
                setNotification({ message: e.message || "Error loading profile", type: "error" });
            } finally {
                setLoading(false);
            }
        })();
    }, [loggedInUser?.email, setNotification]);

    const handleProfileUpdate = async (e) => {
        e.preventDefault();


        const profileForm = {
            full_name: fullName,
            address1,
            address2,
            city,
            state: stateCode,
            zip_code: zip,
            skills,
            preferences,
            availability,
        };

        try {
            const res = await fetch(`http://localhost:5001/profile/${encodeURIComponent(loggedInUser.email)}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(profileForm),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data?.message);

            setLoggedInUser({ ...loggedInUser, profileComplete: true });
            setNotification({ message: "Profile updated successfully!", type: "success" });
            setPage("home");
        } catch (e) {
            setNotification({ message: e.message || "Profile update failed", type: "error" });
        }
    };

    const addAvailabilityDate = () => {
        const dateInput = document.getElementById('availability-date');
        if (dateInput.value && !availability.includes(dateInput.value)) {
            setAvailability([...availability, dateInput.value].sort());
            dateInput.value = '';
        }
    };

    const removeAvailabilityDate = (dateToRemove) => {
        setAvailability(availability.filter(date => date !== dateToRemove));
    };

    return (
        <div className="content-card">
            <h2>{loggedInUser?.profileComplete ? "Edit Your Profile" : "Complete Your Profile"}</h2>
            <p>This information helps us match you with the right events.</p>

            <form onSubmit={handleProfileUpdate} className="form-grid">
                <div className="form-grid-col-span-2">
                    <label className="form-label">Full Name</label>
                    <input type="text" maxLength="50" required className="form-input-full" value={fullName} onChange={(e) => setFullName(e.target.value)} />
                </div>
                <div>
                    <label className="form-label">Address 1</label>
                    <input type="text" maxLength="100" required className="form-input-full" value={address1} onChange={(e) => setAddress1(e.target.value)} />
                </div>
                <div>
                    <label className="form-label">Address 2 (Optional)</label>
                    <input type="text" maxLength="100" className="form-input-full" value={address2} onChange={(e) => setAddress2(e.target.value)} />
                </div>
                <div>
                    <label className="form-label">City</label>
                    <input type="text" maxLength="100" required className="form-input-full" value={city} onChange={(e) => setCity(e.target.value)} />
                </div>
                <div>
                    <label className="form-label">State</label>
                    <select required className="form-select" value={stateCode} onChange={(e) => setStateCode(e.target.value)}>
                        <option value="">Select a State</option>
                        {US_STATES.map(state => <option key={state.code} value={state.code}>{state.name}</option>)}
                    </select>
                </div>
                <div>
                    <label className="form-label">Zip Code</label>
                    <input type="text" minLength="5" maxLength="9" required className="form-input-full" value={zip} onChange={(e) => setZip(e.target.value)} />
                </div>
                <div className="form-grid-col-span-2">
                    <label className="form-label">Skills</label>
                    <CustomMultiSelect options={SKILLS_LIST} selected={skills} onChange={setSkills} placeholder="Select your skills" />
                </div>
                <div className="form-grid-col-span-2">
                    <label className="form-label">Preferences (Optional)</label>
                    <textarea rows="4" className="form-textarea" value={preferences} onChange={(e) => setPreferences(e.target.value)} ></textarea>
                </div>
                <div className="form-grid-col-span-2">
                    <label className="form-label">Availability</label>
                    <div className="availability-controls">
                        <input type="date" id="availability-date" className="form-input-full availability-input" />
                        <button type="button" onClick={addAvailabilityDate} className="button-add">Add Date</button>
                    </div>
                    <div className="availability-tags">
                        {availability.map(date => (
                            <div key={date} className="availability-tag">
                                {date}
                                <button type="button" onClick={() => removeAvailabilityDate(date)}>
                                    <XIcon className="availability-tag-icon" />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
                <div className="form-grid-col-span-2 form-actions">
                    <button type="submit" className="button-submit">Save Profile</button>
                </div>
            </form>
        </div>
    );
};

// helper to pretty-date
const fmt = (dStr) => new Date(dStr).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });

function EventDetail({ event, onBack, loggedInUser, setNotification }) {
    const [localEvent, setLocalEvent] = useState(event || {});
    const [displayNames, setDisplayNames] = useState([]);

    useEffect(() => {
        if (!event?.id) return;
        let cancelled = false;

        (async () => {
            try {
                const res = await fetch(`http://localhost:5001/events/${event.id}`);
                const data = await res.json();
                if (!res.ok) throw new Error(data?.message || 'Failed to load event');
                if (!cancelled) setLocalEvent(data);
            } catch (err) {
            }
        })();

        return () => { cancelled = true; };
    }, [event?.id]);


    // Helper to format as "First L."
    const abbrevName = (full) => {
        if (!full || typeof full !== 'string') return '';
        const parts = full.trim().split(/\s+/);
        if (parts.length === 1) return parts[0]; // single name
        const first = parts[0];
        const last = parts[parts.length - 1];
        return `${first} ${last.charAt(0).toUpperCase()}.`;
    };

    // Resolve participants' full names -> "John S."
    useEffect(() => {
        const participants = localEvent.participants || [];
        if (!participants.length) {
            setDisplayNames([]);
            return;
        }

        let cancelled = false;
        (async () => {
            try {
                // fetch full_name by email
                const profiles = await Promise.all(
                    participants.map(async (email) => {
                        const res = await fetch(`http://localhost:5001/profile/${encodeURIComponent(email)}`);
                        if (!res.ok) return { email, full_name: '' };
                        const p = await res.json();
                        return { email, full_name: p.full_name || '' };
                    })
                );
                if (!cancelled) {
                    const names = profiles
                        .map(p => p.full_name ? abbrevName(p.full_name) : p.email)
                        .filter(Boolean);
                    setDisplayNames(names);
                }
            } catch {
                // If profiles fail, just show emails, maybe delete later if it's too much idk
                if (!cancelled) setDisplayNames(participants);
            }
        })();

        return () => { cancelled = true; };
    }, [localEvent.participants]);

    if (!localEvent?.id) {
        return (
            <div className="content-card">
                <h2>Event not found</h2>
                <p>We couldn’t load this event.</p>
                <div className="form-actions">
                    <button type="button" className="button-add" onClick={onBack}>Back to Events</button>
                </div>
            </div>
        );
    }

    const isAdmin = loggedInUser?.role === 'admin';
    const eventDateStr = localEvent.date || localEvent.event_date;
    const eventDate = eventDateStr ? new Date(eventDateStr) : null;
    const isPast = eventDate ? eventDate < new Date() : false;

    const handleJoin = async () => {
        if (isPast) return;
        try {
            const res = await fetch(`http://localhost:5001/events/${localEvent.id}/join`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: loggedInUser.email })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data?.message || 'Join failed');

            // Server returns the updated event + participants
            const updated = data.event || {};
            setLocalEvent(prev => ({ ...prev, participants: updated.participants || [] }));

            setNotification?.({ message: 'You have joined this event!', type: 'success' });
        } catch (err) {
            setNotification?.({ message: err.message || 'Failed to join event', type: 'error' });
        }
    };

    return (
        <div className="content-card">
            <h2 style={{ color: '#BD0000' }}>{localEvent.name}</h2>
            <p><strong>Date:</strong> {fmt(localEvent.event_date)}</p>
            <p><strong>Urgency:</strong> {localEvent.urgency}</p>
            <p style={{ whiteSpace: 'pre-wrap' }}><strong>Description:</strong> {localEvent.description}</p>
            <p style={{ whiteSpace: 'pre-wrap' }}><strong>Location:</strong> {localEvent.location}</p>
            <p>
                <strong>Required Skills:</strong>{' '}
                {localEvent.requiredSkills?.length ? localEvent.requiredSkills.join(', ') : 'None'}
            </p>

            <p style={{ marginTop: '0.75rem' }}>
                <strong>Volunteers:</strong>{' '}
                {displayNames.length ? displayNames.join(', ') : 'None yet'}
            </p>

            <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {/* Non-admin view */}
                {!isAdmin && (
                    <button
                        className="button-submit"
                        type="button"
                        disabled={isPast}
                        title={isPast ? 'Volunteering opportunity closed' : 'Volunteer for this event'}
                        style={{
                            opacity: isPast ? 0.5 : 1,
                            cursor: isPast ? 'not-allowed' : 'pointer',
                            backgroundColor: isPast ? '#9ca3af' : '#b91c1c' // grey if closed
                        }}
                        onClick={() => {
                            if (isPast) return;
                            handleJoin();
                        }}
                    >
                        {isPast ? 'Volunteering opportunity closed' : 'Volunteer for this Event'}
                    </button>
                )}

                {/* Admin view */}
                {isAdmin && (
                    <button
                        className="button-add"
                        type="button"
                        onClick={() => {
                            // placeholder, figure out later
                            alert('End Event placeholder clicked');
                        }}
                    >
                        End Event
                    </button>
                )}
            </div>

            <div className="form-actions" style={{ marginTop: '1rem' }}>
                <button type="button" className="button-add" onClick={onBack}>Back to Events</button>
            </div>
        </div>
    );
}



const EventManagementPage = ({ setPage, setNotification }) => {
    const [requiredSkills, setRequiredSkills] = useState([]);

    const handleEventCreation = async (e) => {
        e.preventDefault();

        // Build payload in the shape Flask expects
        const formData = new FormData(e.target);
        //Get form data and match it to flask names
        const eventFormData = {
            event_name: formData.get('name'),
            description: formData.get('description'),
            location: formData.get('location'),
            required_skills: requiredSkills,
            urgency: formData.get('urgency'),
            event_date: formData.get('date'),
        };

        try {
            //Set up post
            const res = await fetch('http://localhost:5001/events', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(eventFormData),
            });
            const data = await res.json();
            //Try to post
            if (!res.ok) throw new Error(data?.message || 'Request failed');

            setPage('eventList');
        } catch (err) {
            console.error(err);
            setNotification({ message: `Create failed: ${err.message}`, type: 'error' });
        }
    };


    return (
        <div className="content-card">
            <h2>Create a New Event</h2>
            <p>Fill out the details below to post a new event for volunteers.</p>

            <form onSubmit={handleEventCreation} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div>
                    <label className="form-label">Event Name</label>
                    <input name="name" type="text" maxLength="100" required className="form-input-full" />
                </div>
                <div>
                    <label className="form-label">Event Description</label>
                    <textarea name="description" rows="5" required className="form-textarea"></textarea>
                </div>
                <div>
                    <label className="form-label">Location</label>
                    <textarea name="location" rows="3" required className="form-textarea"></textarea>
                </div>
                <div className="form-grid form-grid-cols-3">
                    <div>
                        <label className="form-label">Required Skills</label>
                        <CustomMultiSelect options={SKILLS_LIST} selected={requiredSkills} onChange={setRequiredSkills} placeholder="Select required skills" />
                    </div>
                    <div>
                        <label className="form-label">Urgency</label>
                        <select name="urgency" required className="form-select">
                            <option value="">Select Urgency</option>
                            {URGENCY_LEVELS.map(level => <option key={level} value={level}>{level}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="form-label">Event Date</label>
                        <input name="date" type="date" required className="form-input-full" />
                    </div>
                </div>
                <div className="form-actions">
                    <button type="submit" className="button-submit">Create Event</button>
                </div>
            </form>
        </div>
    );
}

const HomePage = () => (
    <div style={{ textAlign: 'center', marginTop: '5rem' }}>
        <h1 style={{ fontSize: '3rem', fontWeight: 'bold', color: '#1f2937' }}>Event Management Hub</h1>
        <p style={{ fontSize: '1.25rem', color: '#6b7280', marginTop: '1rem' }}>Connecting volunteers with opportunities.</p>
    </div>
);

// Page Components
export default function App() {
    const [page, setPage] = useState('home');
    const [loggedInUser, setLoggedInUser] = useState(null);
    const [notification, setNotification] = useState(null);
    const [events, setEvents] = useState([]);
    const [focusedEvent, setFocusedEvent] = useState(null);

    const handleLogout = () => {
        setLoggedInUser(null);
        setPage('home');
    };

    const renderPage = () => {
        switch (page) {
            case 'login':
                return <LoginPage setPage={setPage} setLoggedInUser={setLoggedInUser} setNotification={setNotification} />;
            case 'register':
                return <RegisterPage setPage={setPage} setLoggedInUser={setLoggedInUser} setNotification={setNotification} />;
            case 'profile':
                if (!loggedInUser) {
                    setPage('login');
                    return null;
                }
                return <ProfilePage setPage={setPage} loggedInUser={loggedInUser} setLoggedInUser={setLoggedInUser} setNotification={setNotification} />;
            case 'eventManagement':
                if (!loggedInUser || loggedInUser.role !== 'admin') {
                    console.warn("Attempted to access admin page without being logged in as admin.");
                }
                return <EventManagementPage setPage={setPage} setNotification={setNotification} setEvents={setEvents} />;
            case 'eventList':
                if (!loggedInUser) { setPage('login'); return null; }
                return <EventList onSelect={(ev) => { setFocusedEvent(ev); setPage('eventDetail'); }} />;
            case 'eventDetail':
                if (!loggedInUser) { setPage('login'); return null; }
                return (
                    <EventDetail event={focusedEvent} onBack={() => setPage('eventList')} loggedInUser={loggedInUser} setNotification={setNotification} />
                )
            case 'home':
            default:
                return <HomePage />;
        }
    };
    return (
        <div className="app-container">
            <AppStyles /> {/* Add the styles component here */}
            <Notification message={notification?.message} type={notification?.type} onClose={() => setNotification(null)} />
            <nav className="navbar">
                <div className="nav-container">
                    <div>
                        <button onClick={() => setPage('home')} className="nav-brand">
                            EventApp
                        </button>
                    </div>
                    <div className="nav-links">
                        <button onClick={() => setPage('home')} className="nav-button">Home</button>

                        {loggedInUser ? (
                            <>
                                <button onClick={() => setPage('eventList')} className="nav-button">EventList</button>
                                {loggedInUser.role === 'admin' ? (
                                    <button onClick={() => setPage('eventManagement')} className="nav-button">Event Management</button>
                                ) : (
                                    <button onClick={() => setPage('profile')} className="nav-button">Profile</button>
                                )}
                                <button onClick={handleLogout} className="nav-button-secondary">Logout</button>
                            </>
                        ) : (
                            <>
                                <button onClick={() => setPage('login')} className="nav-button">Login</button>
                                <button onClick={() => setPage('register')} className="nav-button-primary">Register</button>
                            </>
                        )}
                    </div>
                </div>
            </nav>
            <main className="main-content">
                {renderPage()}
            </main>
        </div>
    );
}

