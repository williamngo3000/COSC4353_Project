import React, { useState, useEffect } from 'react';

export default function VolunteerMatchingPage({ setNotification }) {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [matches, setMatches] = useState([]);

  // Load all events
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("http://localhost:5001/events");
        if (!res.ok) throw new Error("Failed to load events");
        const data = await res.json();
        setEvents(data);
      } catch (err) {
        setNotification({ message: err.message, type: "error" });
      }
    })();
  }, [setNotification]);

  const handleMatchSearch = async (eventId) => {
    try {
      setSelectedEvent(eventId);
      const res = await fetch(`http://localhost:5001/matching/${eventId}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data?.message || "Failed to fetch matches");
      setMatches(data);
      setNotification({ message: "Matches loaded successfully!", type: "success" });
    } catch (err) {
      setNotification({ message: err.message, type: "error" });
    }
  };

  return (
    <div className="content-card">
      <h2>Volunteer Matching</h2>
      <p>Select an event to view matching volunteers based on skills and availability.</p>

      <div style={{ marginBottom: "2rem" }}>
        <label className="form-label">Choose an Event</label>
        <select
          className="form-select"
          onChange={(e) => handleMatchSearch(e.target.value)}
          defaultValue=""
        >
          <option value="">Select Event</option>
          {events.map((event) => (
            <option key={event.id} value={event.id}>
              {event.event_name} — {event.event_date}
            </option>
          ))}
        </select>
      </div>

      {selectedEvent && (
        <>
          <h3 style={{ marginBottom: "1rem" }}>Matching Volunteers</h3>
          {matches.length > 0 ? (
            <ul style={{ listStyle: "none", padding: 0 }}>
              {matches.map((vol) => (
                <li
                  key={vol.email}
                  style={{
                    background: "#f3f4f6",
                    padding: "1rem",
                    borderRadius: "0.5rem",
                    marginBottom: "1rem",
                  }}
                >
                  <strong>{vol.full_name}</strong> ({vol.email})<br />
                  <span style={{ color: "#6b7280" }}>
                    Skills: {vol.skills.join(", ")}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ color: "#6b7280" }}>No volunteers match this event’s requirements.</p>
          )}
        </>
      )}
    </div>
  );
}

