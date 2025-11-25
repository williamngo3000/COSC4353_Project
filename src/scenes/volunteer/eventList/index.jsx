import { useEffect, useState } from 'react';

const EventList = ({ addNotification }) => {
    const [events, setEvents] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [requestedEvents, setRequestedEvents] = useState(new Set());
    const [acceptedEvents, setAcceptedEvents] = useState(new Set());
    const [completedEvents, setCompletedEvents] = useState(new Set());
    const [searchTerm, setSearchTerm] = useState('');
    const [filterUrgency, setFilterUrgency] = useState('');

    const fetchEvents = () => {
        fetch('http://localhost:5001/events')
            .then(res => {
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                const formatted = data.map(ev => ({
                    id: ev.id,
                    name: ev.event_name,
                    description: ev.description,
                    location: ev.location,
                    requiredSkills: ev.required_skills,
                    urgency: ev.urgency,
                    date: ev.event_date,
                    volunteerLimit: ev.volunteer_limit,
                    currentVolunteers: ev.current_volunteers,
                    status: ev.status,
                }));
                setEvents(formatted);
                setError(null);
                setLoading(false);
            })
            .catch(err => {
                console.error('Failed to load events:', err);
                setError(err.message);
                setLoading(false);
            });
    };

    const fetchUserInvites = async () => {
        const userEmail = localStorage.getItem('userEmail');
        if (!userEmail) return;

        try {
            const response = await fetch(`http://localhost:5001/invites/user/${encodeURIComponent(userEmail)}`);
            if (response.ok) {
                const invites = await response.json();

                // Track pending requests
                const pending = new Set(
                    invites
                        .filter(inv => inv.status === 'pending')
                        .map(inv => inv.event_id)
                );
                setRequestedEvents(pending);

                // Track accepted invites that are not completed
                const accepted = new Set(
                    invites
                        .filter(inv => inv.status === 'accepted' && !inv.completed)
                        .map(inv => inv.event_id)
                );
                setAcceptedEvents(accepted);

                // Track completed events
                const completed = new Set(
                    invites
                        .filter(inv => inv.status === 'accepted' && inv.completed)
                        .map(inv => inv.event_id)
                );
                setCompletedEvents(completed);
            }
        } catch (error) {
            console.error('Error fetching user invites:', error);
        }
    };

    useEffect(() => {
        // Initial fetch
        fetchEvents();
        fetchUserInvites();

        // Set up polling - refresh every 5 seconds
        const interval = setInterval(() => {
            fetchEvents();
            fetchUserInvites();
        }, 5000);

        // Clean up interval on unmount
        return () => clearInterval(interval);
    }, []);

    const handleRequestToJoin = async (eventId, eventName) => {
        const userEmail = localStorage.getItem('userEmail');

        if (!userEmail) {
            addNotification('Please log in to request to join an event', 'error');
            return;
        }

        try {
            const response = await fetch('http://localhost:5001/invites', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    event_id: eventId,
                    email: userEmail,
                    type: 'user_request'
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                // Show the backend error message as a notification
                addNotification(data.message || 'Failed to send request', 'error');
                return;
            }

            // Optimistically update UI
            setRequestedEvents(prev => new Set([...prev, eventId]));
            addNotification(`Successfully requested to join "${eventName}"`, 'success');

            // Refresh to get latest state
            fetchUserInvites();
        } catch (error) {
            console.error('Error sending request:', error);
            addNotification('Failed to send request. Please try again.', 'error');
        }
    };

    const handleCancelRequest = async (eventId, eventName) => {
        const userEmail = localStorage.getItem('userEmail');

        if (!userEmail) {
            addNotification('Please log in to cancel your request', 'error');
            return;
        }

        if (!confirm(`Are you sure you want to cancel your signup for "${eventName}"?`)) {
            return;
        }

        try {
            // Find the invite ID for this user and event
            const response = await fetch(`http://localhost:5001/invites/user/${encodeURIComponent(userEmail)}`);
            if (!response.ok) {
                throw new Error('Failed to fetch invites');
            }

            const invites = await response.json();
            const invite = invites.find(inv => inv.event_id === eventId && inv.status !== 'declined');

            if (!invite) {
                addNotification('No active signup found for this event', 'error');
                return;
            }

            // Delete the invite
            const deleteResponse = await fetch(`http://localhost:5001/invites/${invite.id}`, {
                method: 'DELETE',
            });

            if (!deleteResponse.ok) {
                throw new Error('Failed to cancel signup');
            }

            // Update UI
            setRequestedEvents(prev => {
                const newSet = new Set(prev);
                newSet.delete(eventId);
                return newSet;
            });
            setAcceptedEvents(prev => {
                const newSet = new Set(prev);
                newSet.delete(eventId);
                return newSet;
            });

            addNotification(`Successfully cancelled your signup for "${eventName}"`, 'success');

            // Refresh to get latest state
            fetchUserInvites();
        } catch (error) {
            console.error('Error cancelling request:', error);
            addNotification('Failed to cancel signup. Please try again.', 'error');
        }
    };

    if (loading) {
        return (
            <div style={{ textAlign: 'center', marginTop: '5rem' }}>
                <h1 style={{ fontSize: '3rem', fontWeight: 'bold', color: '#1f2937' }}>Event List:</h1>
                <p style={{ fontSize: '1.5rem', color: '#6b7280', marginTop: '2rem' }}>Loading events...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ textAlign: 'center', marginTop: '5rem' }}>
                <h1 style={{ fontSize: '3rem', fontWeight: 'bold', color: '#1f2937' }}>Event List:</h1>
                <p style={{ fontSize: '1.5rem', color: '#ef4444', marginTop: '2rem' }}>Failed to fetch events: {error}</p>
                <button
                    onClick={fetchEvents}
                    style={{
                        marginTop: '1rem',
                        padding: '0.5rem 1rem',
                        backgroundColor: '#BD0000',
                        color: 'white',
                        border: 'none',
                        borderRadius: '0.25rem',
                        cursor: 'pointer'
                    }}
                >
                    Retry
                </button>
            </div>
        );
    }

    // Filter events based on search and filters
    const filteredEvents = events.filter(ev => {
        const matchesSearch = ev.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                              ev.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                              ev.location?.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesUrgency = !filterUrgency || ev.urgency === filterUrgency;

        return matchesSearch && matchesUrgency;
    });

    return (
        <div style={{ textAlign: 'center', marginTop: '5rem' }}>
            <h1 style={{ fontSize: '3rem', fontWeight: 'bold', color: '#1f2937' }}>Event List:</h1>

            {/* Search and Filter Section */}
            <div style={{
                display: 'flex',
                gap: '1rem',
                justifyContent: 'center',
                alignItems: 'center',
                marginTop: '2rem',
                marginBottom: '1rem',
                flexWrap: 'wrap'
            }}>
                <input
                    type="text"
                    placeholder="Search events..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{
                        padding: '0.75rem',
                        fontSize: '1rem',
                        border: '2px solid #d1d5db',
                        borderRadius: '0.5rem',
                        minWidth: '300px',
                        outline: 'none',
                        transition: 'border-color 0.2s',
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#BD0000'}
                    onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
                />
                <select
                    value={filterUrgency}
                    onChange={(e) => setFilterUrgency(e.target.value)}
                    style={{
                        padding: '0.75rem',
                        fontSize: '1rem',
                        border: '2px solid #d1d5db',
                        borderRadius: '0.5rem',
                        minWidth: '150px',
                        outline: 'none',
                        cursor: 'pointer',
                        backgroundColor: 'white'
                    }}
                >
                    <option value="">All Urgencies</option>
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Critical">Critical</option>
                </select>
                {(searchTerm || filterUrgency) && (
                    <button
                        onClick={() => {
                            setSearchTerm('');
                            setFilterUrgency('');
                        }}
                        style={{
                            padding: '0.75rem 1.5rem',
                            fontSize: '1rem',
                            backgroundColor: '#6b7280',
                            color: 'white',
                            border: 'none',
                            borderRadius: '0.5rem',
                            cursor: 'pointer',
                            fontWeight: '500'
                        }}
                    >
                        Clear Filters
                    </button>
                )}
            </div>

            {events.length === 0 ? (
                <p style={{ fontSize: '1.5rem', color: '#6b7280', marginTop: '2rem' }}>No current events</p>
            ) : filteredEvents.length === 0 ? (
                <p style={{ fontSize: '1.5rem', color: '#6b7280', marginTop: '2rem' }}>No events match your search criteria</p>
            ) : (
                [...filteredEvents].sort((a, b) => new Date(a.date) - new Date(b.date)).map(ev => (
                    <div key={ev.id} className="border border-gray-300 rounded-lg p-4 my-4 shadow-sm bg-white">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#BD0000' }}> {ev.name} </h2>
                            {ev.status === 'closed' && (
                                <span style={{
                                    padding: '0.25rem 0.75rem',
                                    backgroundColor: '#dc2626',
                                    color: 'white',
                                    borderRadius: '9999px',
                                    fontSize: '0.75rem',
                                    fontWeight: '600'
                                }}>
                                    CLOSED
                                </span>
                            )}
                        </div>
                        <div className="text-sm font-medium text-gray-800 space-y-1">
                            <p>Description: {ev.description}</p>
                            <p>Location: {ev.location}</p>
                            <div>
                                {ev.requiredSkills ? (
                                    <p>Required Skills: {Array.isArray(ev.requiredSkills) ? ev.requiredSkills.join(', ') : ev.requiredSkills}</p>
                                ) : (
                                    <p>Required Skills: None</p>
                                )}
                            </div>
                            <p>Urgency: {ev.urgency}</p>
                            <p>Date: {ev.date}</p>
                            <p style={{ color: ev.status === 'closed' ? '#dc2626' : '#374151' }}>
                                Volunteers: {ev.currentVolunteers || 0}
                                {ev.volunteerLimit ? `/${ev.volunteerLimit}` : ' (unlimited)'}
                            </p>
                        </div>
                        <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                            {ev.status === 'closed' ? (
                                <button
                                    disabled
                                    style={{
                                        padding: '0.5rem 1rem',
                                        backgroundColor: '#6b7280',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '0.25rem',
                                        cursor: 'not-allowed',
                                        fontSize: '0.875rem',
                                        fontWeight: '500',
                                        flex: 1
                                    }}
                                >
                                    Event Closed
                                </button>
                            ) : completedEvents.has(ev.id) ? (
                                <button
                                    disabled
                                    style={{
                                        padding: '0.5rem 1rem',
                                        backgroundColor: '#16a34a',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '0.25rem',
                                        cursor: 'not-allowed',
                                        fontSize: '0.875rem',
                                        fontWeight: '500',
                                        flex: 1
                                    }}
                                >
                                    Completed ✓
                                </button>
                            ) : acceptedEvents.has(ev.id) ? (
                                <>
                                    <button
                                        disabled
                                        style={{
                                            padding: '0.5rem 1rem',
                                            backgroundColor: '#16a34a',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '0.25rem',
                                            cursor: 'not-allowed',
                                            fontSize: '0.875rem',
                                            fontWeight: '500',
                                            flex: 1
                                        }}
                                    >
                                        Signed Up ✓
                                    </button>
                                    <button
                                        onClick={() => handleCancelRequest(ev.id, ev.name)}
                                        style={{
                                            padding: '0.5rem 1rem',
                                            backgroundColor: '#dc2626',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '0.25rem',
                                            cursor: 'pointer',
                                            fontSize: '0.875rem',
                                            fontWeight: '500'
                                        }}
                                    >
                                        Cancel
                                    </button>
                                </>
                            ) : requestedEvents.has(ev.id) ? (
                                <>
                                    <button
                                        disabled
                                        style={{
                                            padding: '0.5rem 1rem',
                                            backgroundColor: '#6b7280',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '0.25rem',
                                            cursor: 'not-allowed',
                                            fontSize: '0.875rem',
                                            fontWeight: '500',
                                            flex: 1
                                        }}
                                    >
                                        Request Pending
                                    </button>
                                    <button
                                        onClick={() => handleCancelRequest(ev.id, ev.name)}
                                        style={{
                                            padding: '0.5rem 1rem',
                                            backgroundColor: '#dc2626',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '0.25rem',
                                            cursor: 'pointer',
                                            fontSize: '0.875rem',
                                            fontWeight: '500'
                                        }}
                                    >
                                        Cancel
                                    </button>
                                </>
                            ) : (
                                <button
                                    onClick={() => handleRequestToJoin(ev.id, ev.name)}
                                    style={{
                                        padding: '0.5rem 1rem',
                                        backgroundColor: '#BD0000',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '0.25rem',
                                        cursor: 'pointer',
                                        fontSize: '0.875rem',
                                        fontWeight: '500',
                                        flex: 1
                                    }}
                                >
                                    Sign up
                                </button>
                            )}
                        </div>
                    </div>
                ))
            )}
        </div>
    );
};

export default EventList;
