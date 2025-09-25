import { useData } from "../store.js";
import eventsData from "../data/eventFake.js"; // optional: seed

export default function History() {
  const { history, addHistory } = useData();

  // Seed button to demonstrate a row in history quickly
  const seed = () => {
    const e = eventsData?.[0] || { name: "Sample Event", date: "2025-10-01", status: "completed" };
    addHistory(e);
  };

  return (
    <div>
      <h2>Volunteer History</h2>
      <button onClick={seed}>Add sample history row</button>
      {history.length === 0 ? <p>No history yet.</p> :
        <table style={{width:"100%", borderCollapse:"collapse", marginTop:12}}>
          <thead><tr>
            <th style={{textAlign:"left"}}>Event</th>
            <th>Date</th>
            <th>Status</th>
          </tr></thead>
          <tbody>
            {history.map((h,i)=>(
              <tr key={i}>
                <td>{h.name}</td>
                <td>{h.date}</td>
                <td>{h.status || "completed"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      }
    </div>
  );
}

