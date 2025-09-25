import { useData } from "../store.js";

export default function Notifications() {
  const { notifications } = useData();
  return (
    <div>
      <h2>Notifications</h2>
      {notifications.length === 0 ? <p>No notifications.</p> :
        <ul>
          {notifications.map(n => (
            <li key={n.id}>{new Date(n.ts).toLocaleString()} — {n.msg}</li>
          ))}
        </ul>
      }
    </div>
  );
}

