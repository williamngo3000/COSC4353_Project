import React from 'react';


export default function EventList({ events }) {
	return (
	<div style={{ textAlign: 'center', marginTop: '5rem' }}>
			<h1 style={{ fontSize: '3rem', fontWeight: 'bold', color: '#1f2937' }}>Event List:</h1>
			{[...events].sort((a, b) => new Date(a.date) - new Date(b.date)).map(ev => (
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
			))}
	</div>
	);
}
