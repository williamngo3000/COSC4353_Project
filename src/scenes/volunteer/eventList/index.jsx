import { useEffect, useState } from 'react';

const EventList = () => {
    const [events, setEvents] = useState([]);

    const fetchEvents = () => {
        fetch('http://localhost:5001/events')
            .then(res => res.json())
            .then(data => {
                const formatted = data.map(ev => ({
                    id: ev.id,
                    name: ev.event_name,
                    description: ev.description,
                    location: ev.location,
                    requiredSkills: ev.required_skills,
                    urgency: ev.urgency,
                    date: ev.event_date,
                }));
                setEvents(formatted);
            })
            .catch(err => console.error('Failed to load events:', err));
    };

    useEffect(() => {
        // Initial fetch
        fetchEvents();

        // Set up polling - refresh every 5 seconds
        const interval = setInterval(fetchEvents, 5000);

        // Clean up interval on unmount
        return () => clearInterval(interval);
    }, []);

    return (
        <div style={{ textAlign: 'center', marginTop: '5rem' }}>
            <h1 style={{ fontSize: '3rem', fontWeight: 'bold', color: '#1f2937' }}>Event List:</h1>
            {events.length === 0 ? (
                <p style={{ fontSize: '1.5rem', color: '#6b7280', marginTop: '2rem' }}>No current events</p>
            ) : (
                [...events].sort((a, b) => new Date(a.date) - new Date(b.date)).map(ev => (
                    <div key={ev.id} className="border border-gray-300 rounded-lg p-4 my-4 shadow-sm bg-white">
                        <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#BD0000' }}> {ev.name} </h2>
                        <div className="text-sm font-medium text-gray-800 space-y-1">
                            <p>Description: {ev.description}</p>
                            <p>Location: {ev.location}</p>
                            <div>
                                {ev.requiredSkills?.length ? (
                                    <p>Required Skills: {ev.requiredSkills.join(', ')}</p>
                                ) : (
                                    <p>Required Skills: None</p>
                                )}
                            </div>
                            <p>Urgency: {ev.urgency}</p>
                            <p>Date: {ev.date}</p>
                        </div>
                    </div>
                ))
            )}
        </div>
    );
};

export default EventList;
