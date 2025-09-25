import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

function Home() {
  return <h1>Welcome to Volunteer Manager</h1>;
}

function MapPlaceholder() {
  return (
    <div style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "80vh"
    }}>
      <div style={{
        width: "600px",
        height: "400px",
        border: "2px solid black",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#f0f0f0"
      }}>
        <h2>Google Maps Placeholder</h2>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <nav style={{ display: "flex", gap: "12px", padding: "10px" }}>
        <Link to="/">Home</Link>
        <Link to="/map">Map</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/map" element={<MapPlaceholder />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

