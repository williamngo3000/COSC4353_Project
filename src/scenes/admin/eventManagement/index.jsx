import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CustomMultiSelect from '../../../components/CustomMultiSelect';
import { SKILLS_LIST, URGENCY_LEVELS } from '../../../utils/constants';
import { useTheme } from '@mui/material/styles';

const EventManagementPage = ({ addNotification }) => {
    const navigate = useNavigate();
    const [requiredSkills, setRequiredSkills] = useState([]);

    const theme = useTheme();
    const isDark = theme.palette.mode === 'dark';
    const textColor = isDark ? '#fff' : '#000';
    const bgColor = isDark ? '#0d1227ff' : '#fff';
    const cardColor = isDark ? '#191e2eff' : '#f8f8f8';

    const handleEventCreation = async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        const volunteerLimit = formData.get('volunteer_limit');
        const eventFormData = {
            event_name: formData.get('name'),
            description: formData.get('description'),
            location: formData.get('location'),
            required_skills: requiredSkills,
            urgency: formData.get('urgency'),
            event_date: formData.get('date'),
            volunteer_limit: volunteerLimit ? parseInt(volunteerLimit) : null,
        };

        try {
            const res = await fetch('http://localhost:5001/events', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(eventFormData),
            });
            const data = await res.json();

            if (!res.ok) throw new Error(data?.message || 'Request failed');

            addNotification("Event created successfully!", "success");
        } catch (err) {
            console.error(err);
            addNotification(`Create failed: ${err.message}`, 'error');
        }
    };

    return (
        <div className="content-card" style={{color: textColor, backgroundColor: cardColor}}>
            <h2 style={{color: textColor}}>Create a New Event</h2>
            <p style={{color: textColor}}>Fill out the details below to post a new event for volunteers.</p>

            <form onSubmit={handleEventCreation} style={{display: 'flex', flexDirection: 'column', gap: '1.5rem', color: textColor}}>
                <div>
                    <label className="form-label" style={{color: textColor}}>Event Name</label>
                    <input name="name" type="text" maxLength="100" required className="form-input-full" style={{color: textColor, backgroundColor: bgColor}} />
                </div>
                <div>
                    <label className="form-label" style={{color: textColor}}>Event Description</label>
                    <textarea name="description" rows="5" required className="form-textarea" style={{color: textColor, backgroundColor: bgColor }}></textarea>
                </div>
                <div>
                    <label className="form-label" style={{color: textColor}}>Location</label>
                    <textarea name="location" rows="3" required className="form-textarea" style={{color: textColor, backgroundColor: bgColor}}></textarea>
                </div>
                <div className="form-grid form-grid-cols-3">
                    <div>
                        <label className="form-label" style={{color: textColor}}>Required Skills</label>
                        <CustomMultiSelect options={SKILLS_LIST} selected={requiredSkills} onChange={setRequiredSkills} placeholder="Select required skills" bgColor={isDark ? '#0d1227ff' : '#fff'}
                            textColor={isDark ? '#fff' : '#000'}
                        
                        />
                    </div>
                    <div>
                        <label className="form-label" style={{color: textColor}}>Urgency</label>
                        <select name="urgency" required className="form-select" style={{color: textColor, backgroundColor: bgColor}}>
                            <option value="">Select Urgency</option>
                            {URGENCY_LEVELS.map(level => <option key={level} value={level}>{level}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="form-label" style={{color: textColor}}>Event Date</label>
                        <input name="date" type="date" required className="form-input-full" style={{color: textColor, backgroundColor: bgColor}}/>
                    </div>
                </div>
                <div>
                    <label className="form-label" style={{color: textColor}}>Volunteer Limit (Optional)</label>
                    <input
                        name="volunteer_limit"
                        type="number"
                        min="1"
                        placeholder="Leave empty for unlimited volunteers"
                        className="form-input-full"
                        style={{color: textColor, backgroundColor: bgColor}}
                    />
                    <small style={{color: isDark ? '#aaa' : '#666', display: 'block', marginTop: '0.25rem'}}>
                        Set a maximum number of volunteers for this event, or leave blank for no limit.
                    </small>
                </div>
                <div className="form-actions">
                    <button type="submit" className="button-submit">Create Event</button>
                </div>
            </form>
        </div>
    );
};

export default EventManagementPage;
