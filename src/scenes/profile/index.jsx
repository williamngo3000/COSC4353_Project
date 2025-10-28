import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CustomMultiSelect from '../../components/CustomMultiSelect';
import { XIcon } from '../../components/Icons';
import { US_STATES, SKILLS_LIST } from '../../utils/constants';

const ProfilePage = ({ loggedInUser, setLoggedInUser, addNotification }) => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);

    // Form state
    const [fullName, setFullName] = useState("");
    const [address1, setAddress1] = useState("");
    const [address2, setAddress2] = useState("");
    const [city, setCity] = useState("");
    const [stateCode, setStateCode] = useState("");
    const [zip, setZip] = useState("");
    const [preferences, setPreferences] = useState("");
    const [skills, setSkills] = useState([]);
    const [availability, setAvailability] = useState([]);

    // Load profile data on mount
    useEffect(() => {
        if (!loggedInUser?.email) {
            navigate('/login');
            return;
        }

        (async () => {
            try {
                const res = await fetch(`http://localhost:5001/profile/${encodeURIComponent(loggedInUser.email)}`);
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
                addNotification(e.message || "Error loading profile", "error");
            } finally {
                setLoading(false);
            }
        })();
    }, [loggedInUser?.email, addNotification, navigate]);

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
            addNotification("Profile updated successfully!", "success");
            navigate("/");
        } catch (e) {
            addNotification(e.message || "Profile update failed", "error");
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

    if (loading) {
        return <div>Loading...</div>;
    }

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
                    <textarea rows="4" className="form-textarea" value={preferences} onChange={(e) => setPreferences(e.target.value)}></textarea>
                </div>
                <div className="form-grid-col-span-2">
                    <label className="form-label">Availability</label>
                    <div className="availability-controls">
                        <input type="date" id="availability-date" className="form-input-full availability-input"/>
                        <button type="button" onClick={addAvailabilityDate} className="button-add">Add Date</button>
                    </div>
                    <div className="availability-tags">
                        {availability.map(date => (
                            <div key={date} className="availability-tag">
                                {date}
                                <button type="button" onClick={() => removeAvailabilityDate(date)}>
                                    <XIcon className="availability-tag-icon"/>
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

export default ProfilePage;
