import React, { useState, useEffect } from 'react';

export default function VolunteerSelfMatch({ loggedInUser, setNotification }) {
  const [matchedEvents, setMatchedEvents] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!loggedInUser?.email) return;

    const fetchMatches = async () => {
      setLoading(true);
      try {
        const res = await fetch(
          `http://localhost:5001/matching/for_volunteer/${encodeURIComponent(
            loggedInUser.email
          )}`
        );
        const data = await res.json();

        if (!res.ok) throw new Error(data?.message || 'Failed to load matches');
        setMatchedEvents(data);
        setNotification({
          message: 'Matched events loaded successfully!',
          type: 'success',
        });
      } catch (err) {
        setNotification({ message: err.message, type: 'error' });
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
  }, [loggedInUser, setNotification]);

  return (
    <div className="content-card">
      <h2>Find Matching Events</h2>
      <p>
        Based on your skills and availability, here are events you’re a great fit
        for!
      </p>

      {loading ? (
        <p>Loading matches...</p>
      ) : matchedEvents.length > 0 ? (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {matchedEvents.map((event) => (
            <li
              key={event.id}
              style={{
                background: '#f3f4f6',
                padding: '1rem',
                borderRadius: '0.5rem',
                marginBottom: '1rem',
              }}
            >
              <strong>{event.event_name}</strong> — {event.event_date}
              <br />
              <span style={{ color: '#6b7280' }}>
                {event.description || 'No description provided'}
              </span>
              <br />
              <span style={{ color: '#9ca3af' }}>
                Skills needed: {event.required_skills?.join(', ') || 'N/A'}
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p style={{ color: '#6b7280' }}>
          No events currently match your profile. Try updating your skills or
          availability!
        </p>
      )}
    </div>
  );
}

