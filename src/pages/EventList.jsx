import React, { useEffect, useState } from 'react';


export default function EventList({ onSelect }) {
	const [events, setEvents] = useState([]);

	useEffect(() => {
		fetch('http://localhost:5001/events')
			.then(res => res.json()) // Read the response and covert to json
			.then(data => {
				// Map flask get, and format it for our page then set it
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
	}, []);

	return (
		<div style={{ textAlign: 'center', marginTop: '5rem' }}>
			<h1 style={{ fontSize: '3rem', fontWeight: 'bold', color: '#1f2937' }}>Event List:</h1>

			{[...events].sort((a, b) => new Date(a.date) - new Date(b.date)).map(ev => {
				const eventDate = new Date(ev.date);
				const isPast = !isNaN(eventDate) && eventDate < new Date();

				return (
					<div
						key={ev.id}
						className="border border-gray-300 rounded-lg p-4 my-4 shadow-sm bg-white"
						onClick={() => { onSelect && onSelect(ev); }}
						style={{
							cursor: 'pointer',
							opacity: isPast ? 0.8 : 1,
							backgroundColor: isPast ? '#a5a5a5ff' : '#ffffff',
							borderColor: isPast ? '#d1d5db' : '#e5e7eb',
							transition: 'opacity 0.2s ease, background-color 0.2s ease',
						}}
					>
						<h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#BD0000' }}>{ev.name}</h2>
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
				);
			})}
		</div>
	);
}
