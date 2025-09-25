import { BrowserRouter, Routes, Route, Navigate, Link } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Profile from "./pages/Profile.jsx";
import EventList from "./pages/EventList.jsx";
import Notifications from "./pages/Notifications.jsx";
import History from "./pages/History.jsx";
import { useAuth } from "./store.js";

function Protected({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function Nav() {
  const { user, logout } = useAuth();
  return (
    <nav style={{display:"flex",gap:12, padding:"10px 16px", borderBottom:"1px solid #eee"}}>
      <Link to="/">Events</Link>
      {user && <Link to="/profile">Profile</Link>}
      {user && <Link to="/notifications">Notifications</Link>}
      {user && <Link to="/history">History</Link>}
      <span style={{marginLeft:"auto"}} />
      {!user && <Link to="/login">Login</Link>}
      {!user && <Link to="/register">Register</Link>}
      {user && <button onClick={logout}>Logout</button>}
    </nav>
  );
}

export default function App() {
  return (
   <> 
      <Nav />
      <div style={{ padding: 16 }}>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/events" element={<EventList />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </div>
    </>
  );
}

