import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const VolunteerNotifications = ({ loggedInUser, addNotification }) => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [upcomingEvents, setUpcomingEvents] = useState([]);
    const [completedEvents, setCompletedEvents] = useState([]);
    const [expiredEvents, setExpiredEvents] = useState([]);
    const [pendingInvites, setPendingInvites] = useState([]);

    useEffect(() => {
        if (!loggedInUser?.email) {
            navigate('/login');
            return;
        }

        fetchUserEvents();
        fetchPendingInvites();

        // Polling for invites every 5 seconds
        const interval = setInterval(fetchPendingInvites, 5000);
        return () => clearInterval(interval);
    }, [loggedInUser?.email, navigate]);

    const fetchPendingInvites = async () => {
        try {
            const userEmail = loggedInUser.email || localStorage.getItem('userEmail');
            if (!userEmail) return;

            const res = await fetch(`http://localhost:5001/invites/user/${encodeURIComponent(userEmail)}?status=pending&type=admin_invite`);

            if (!res.ok) {
                throw new Error('Failed to fetch invites');
            }

            const data = await res.json();
            setPendingInvites(data);
        } catch (error) {
            console.error('Error fetching invites:', error);
        }
    };

    const fetchUserEvents = async () => {
        try {
            // Use email from localStorage if loggedInUser.email is not available
            const userEmail = loggedInUser.email || localStorage.getItem('userEmail');

            if (!userEmail) {
                throw new Error('User email not found. Please log in again.');
            }

            console.log('Fetching events for user:', userEmail);

            const res = await fetch(`http://localhost:5001/user/${encodeURIComponent(userEmail)}/events`);

            if (!res.ok) {
                const errorText = await res.text();
                throw new Error(`Failed to fetch events: ${res.status} ${errorText}`);
            }

            const data = await res.json();

            // Separate events into upcoming, completed, and expired
            const now = new Date();
            const upcoming = data.events.filter(event =>
                new Date(event.event_date) >= now && !event.completed
            );
            const completed = data.events.filter(event => event.completed);
            const expired = data.events.filter(event =>
                new Date(event.event_date) < now && !event.completed
            );

            setUpcomingEvents(upcoming);
            setCompletedEvents(completed);
            setExpiredEvents(expired);
        } catch (error) {
            console.error('Error fetching user events:', error);
            addNotification(error.message || 'Failed to load events', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleAcceptInvite = async (inviteId) => {
        try {
            const response = await fetch(`http://localhost:5001/invites/${inviteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 'accepted' }),
            });

            if (!response.ok) {
                throw new Error('Failed to accept invite');
            }

            // Optimistic update
            setPendingInvites(prev => prev.filter(invite => invite.id !== inviteId));
            addNotification('Invite accepted successfully!', 'success');

            // Refresh events to include the newly accepted event
            fetchUserEvents();
        } catch (error) {
            console.error('Error accepting invite:', error);
            addNotification('Failed to accept invite', 'error');
        }
    };

    const handleDeclineInvite = async (inviteId) => {
        try {
            const response = await fetch(`http://localhost:5001/invites/${inviteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 'declined' }),
            });

            if (!response.ok) {
                throw new Error('Failed to decline invite');
            }

            // Optimistic update
            setPendingInvites(prev => prev.filter(invite => invite.id !== inviteId));
            addNotification('Invite declined', 'info');
        } catch (error) {
            console.error('Error declining invite:', error);
            addNotification('Failed to decline invite', 'error');
        }
    };

    const handleUnregister = async (eventId, eventName) => {
        const userEmail = loggedInUser.email || localStorage.getItem('userEmail');

        if (!userEmail) {
            addNotification('Please log in to unregister from an event', 'error');
            return;
        }

        if (!confirm(`Are you sure you want to unregister from "${eventName}"?`)) {
            return;
        }

        try {
            // Find the invite ID for this user and event
            const response = await fetch(`http://localhost:5001/invites/user/${encodeURIComponent(userEmail)}`);
            if (!response.ok) {
                throw new Error('Failed to fetch invites');
            }

            const invites = await response.json();
            const invite = invites.find(inv => inv.event_id === eventId && inv.status === 'accepted');

            if (!invite) {
                addNotification('No active signup found for this event', 'error');
                return;
            }

            // Delete the invite
            const deleteResponse = await fetch(`http://localhost:5001/invites/${invite.id}`, {
                method: 'DELETE',
            });

            if (!deleteResponse.ok) {
                throw new Error('Failed to unregister from event');
            }

            addNotification(`Successfully unregistered from "${eventName}"`, 'success');

            // Refresh events
            fetchUserEvents();
        } catch (error) {
            console.error('Error unregistering from event:', error);
            addNotification('Failed to unregister. Please try again.', 'error');
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

            {/* Pending Invites Section */}
            {pendingInvites.length > 0 && (
                <div style={{ marginTop: '2rem', marginBottom: '2rem' }}>
                    <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: '600', color: '#dc2626' }}>
                        Pending Invites ({pendingInvites.length})
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {pendingInvites.map((invite) => (
                            <div
                                key={invite.id}
                                style={{
                                    padding: '1.5rem',
                                    border: '2px solid #dc2626',
                                    borderRadius: '0.5rem',
                                    backgroundColor: '#fef2f2',
                                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                                }}
                            >
                                <div style={{ marginBottom: '1rem' }}>
                                    <h4 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                                        {invite.event?.event_name || 'Event Invite'}
                                    </h4>
                                    {invite.event && (
                                        <>
                                            <p style={{ color: '#6b7280', marginBottom: '0.5rem' }}>
                                                {invite.event.description}
                                            </p>
                                            <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.875rem', color: '#4b5563' }}>
                                                <div>
                                                    <strong>Date:</strong> {new Date(invite.event.event_date).toLocaleDateString()}
                                                </div>
                                                <div>
                                                    <strong>Location:</strong> {invite.event.location}
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </div>
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <button
                                        onClick={() => handleAcceptInvite(invite.id)}
                                        style={{
                                            padding: '0.5rem 1rem',
                                            backgroundColor: '#16a34a',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '0.375rem',
                                            cursor: 'pointer',
                                            fontWeight: '600'
                                        }}
                                    >
                                        Accept
                                    </button>
                                    <button
                                        onClick={() => handleDeclineInvite(invite.id)}
                                        style={{
                                            padding: '0.5rem 1rem',
                                            backgroundColor: '#dc2626',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '0.375rem',
                                            cursor: 'pointer',
                                            fontWeight: '600'
                                        }}
                                    >
                                        Decline
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

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
                                            <div style={{ marginTop: '1rem' }}>
                                                <button
                                                    onClick={() => handleUnregister(event.event_id, event.event_name)}
                                                    style={{
                                                        padding: '0.5rem 1rem',
                                                        backgroundColor: '#dc2626',
                                                        color: 'white',
                                                        border: 'none',
                                                        borderRadius: '0.375rem',
                                                        cursor: 'pointer',
                                                        fontWeight: '600',
                                                        fontSize: '0.875rem'
                                                    }}
                                                >
                                                    Unregister
                                                </button>
                                            </div>
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

            {/* Completed Events Section */}
            {completedEvents.length > 0 && (
                <div style={{ marginTop: '3rem' }}>
                    <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: '600', color: '#16a34a' }}>
                        Completed Events ({completedEvents.length})
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {completedEvents.map((event, index) => (
                            <div
                                key={index}
                                style={{
                                    padding: '1.5rem',
                                    border: '2px solid #16a34a',
                                    borderRadius: '0.5rem',
                                    backgroundColor: '#f0fdf4',
                                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div>
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
                                    <span style={{
                                        padding: '0.25rem 0.75rem',
                                        backgroundColor: '#16a34a',
                                        color: 'white',
                                        borderRadius: '9999px',
                                        fontSize: '0.75rem',
                                        fontWeight: '600'
                                    }}>
                                        COMPLETED ✓
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Expired Events Section */}
            {expiredEvents.length > 0 && (
                <div style={{ marginTop: '3rem' }}>
                    <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: '600', color: '#dc2626' }}>
                        Expired Events ({expiredEvents.length})
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {expiredEvents.map((event, index) => (
                            <div
                                key={index}
                                style={{
                                    padding: '1.5rem',
                                    border: '2px solid #dc2626',
                                    borderRadius: '0.5rem',
                                    backgroundColor: '#fef2f2',
                                    opacity: 0.9
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
                                            backgroundColor: '#dc2626',
                                            color: 'white',
                                            borderRadius: '0.375rem',
                                            fontWeight: '600',
                                            fontSize: '0.875rem',
                                            whiteSpace: 'nowrap',
                                            marginLeft: '1rem'
                                        }}
                                    >
                                        EXPIRED
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
