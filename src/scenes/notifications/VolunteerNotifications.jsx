import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const VolunteerNotifications = ({ loggedInUser, addNotification }) => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [upcomingEvents, setUpcomingEvents] = useState([]);
    const [pastEvents, setPastEvents] = useState([]);

    useEffect(() => {
        if (!loggedInUser?.email) {
            navigate('/login');
            return;
        }

        fetchUserEvents();
    }, [loggedInUser?.email, navigate]);

    const fetchUserEvents = async () => {
        try {
            const res = await fetch(`http://localhost:5001/user/${encodeURIComponent(loggedInUser.email)}/events`);
            if (!res.ok) throw new Error('Failed to fetch events');

            const data = await res.json();

            // Separate upcoming and past events
            const now = new Date();
            const upcoming = data.events.filter(event => new Date(event.event_date) >= now);
            const past = data.events.filter(event => new Date(event.event_date) < now);

            setUpcomingEvents(upcoming);
            setPastEvents(past);
        } catch (error) {
            addNotification(error.message || 'Failed to load events', 'error');
        } finally {
            setLoading(false);
        }
    };

    const getDaysUntilEvent = (eventDate) => {
        const now = new Date();
        const event = new Date(eventDate);
        const diffTime = event - now;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    };

    const getUrgencyBadge = (daysUntil) => {
        if (daysUntil === 0) return { text: 'TODAY', color: '#dc2626' };
        if (daysUntil === 1) return { text: 'TOMORROW', color: '#ea580c' };
        if (daysUntil <= 3) return { text: `${daysUntil} DAYS`, color: '#ea580c' };
        if (daysUntil <= 7) return { text: `${daysUntil} DAYS`, color: '#ca8a04' };
        return { text: `${daysUntil} DAYS`, color: '#16a34a' };
    };

    if (loading) {
        return (
            <div className="content-card">
                <h2>Loading notifications...</h2>
            </div>
        );
    }

    return (
        <div className="content-card">
            <h2>My Event Notifications</h2>
            <p>View your upcoming events and reminders</p>

            {/* Upcoming Events Section */}
            <div style={{ marginTop: '2rem' }}>
                <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: '600' }}>
                    Upcoming Events ({upcomingEvents.length})
                </h3>

                {upcomingEvents.length === 0 ? (
                    <div style={{
                        padding: '2rem',
                        textAlign: 'center',
                        backgroundColor: '#f3f4f6',
                        borderRadius: '0.5rem',
                        color: '#6b7280'
                    }}>
                        <p>You have no upcoming events.</p>
                        <button
                            onClick={() => navigate('/eventlist')}
                            style={{
                                marginTop: '1rem',
                                padding: '0.5rem 1rem',
                                backgroundColor: '#dc2626',
                                color: 'white',
                                border: 'none',
                                borderRadius: '0.375rem',
                                cursor: 'pointer'
                            }}
                        >
                            Browse Events
                        </button>
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {upcomingEvents.map((event, index) => {
                            const daysUntil = getDaysUntilEvent(event.event_date);
                            const badge = getUrgencyBadge(daysUntil);

                            return (
                                <div
                                    key={index}
                                    style={{
                                        padding: '1.5rem',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '0.5rem',
                                        backgroundColor: 'white',
                                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                        <div style={{ flex: 1 }}>
                                            <h4 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                                                {event.event_name}
                                            </h4>
                                            <p style={{ color: '#6b7280', marginBottom: '0.5rem' }}>
                                                {event.description}
                                            </p>
                                            <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.875rem', color: '#4b5563' }}>
                                                <div>
                                                    <strong>Date:</strong> {new Date(event.event_date).toLocaleDateString()}
                                                </div>
                                                <div>
                                                    <strong>Location:</strong> {event.location}
                                                </div>
                                            </div>
                                            {event.required_skills && event.required_skills.length > 0 && (
                                                <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                                                    <strong>Skills:</strong> {event.required_skills.join(', ')}
                                                </div>
                                            )}
                                        </div>
                                        <div
                                            style={{
                                                padding: '0.5rem 1rem',
                                                backgroundColor: badge.color,
                                                color: 'white',
                                                borderRadius: '0.375rem',
                                                fontWeight: '600',
                                                fontSize: '0.875rem',
                                                whiteSpace: 'nowrap',
                                                marginLeft: '1rem'
                                            }}
                                        >
                                            {badge.text}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Past Events Section */}
            {pastEvents.length > 0 && (
                <div style={{ marginTop: '3rem' }}>
                    <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: '600' }}>
                        Past Events ({pastEvents.length})
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {pastEvents.map((event, index) => (
                            <div
                                key={index}
                                style={{
                                    padding: '1.5rem',
                                    border: '1px solid #e5e7eb',
                                    borderRadius: '0.5rem',
                                    backgroundColor: '#f9fafb',
                                    opacity: 0.8
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                    <div style={{ flex: 1 }}>
                                        <h4 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                                            {event.event_name}
                                        </h4>
                                        <p style={{ color: '#6b7280', marginBottom: '0.5rem' }}>
                                            {event.description}
                                        </p>
                                        <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.875rem', color: '#4b5563' }}>
                                            <div>
                                                <strong>Date:</strong> {new Date(event.event_date).toLocaleDateString()}
                                            </div>
                                            <div>
                                                <strong>Location:</strong> {event.location}
                                            </div>
                                        </div>
                                    </div>
                                    <div
                                        style={{
                                            padding: '0.5rem 1rem',
                                            backgroundColor: '#6b7280',
                                            color: 'white',
                                            borderRadius: '0.375rem',
                                            fontWeight: '600',
                                            fontSize: '0.875rem',
                                            whiteSpace: 'nowrap',
                                            marginLeft: '1rem'
                                        }}
                                    >
                                        COMPLETED
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default VolunteerNotifications;
