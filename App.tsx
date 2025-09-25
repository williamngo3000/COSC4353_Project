import React from "react";

function App() {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: "#f5f5f5",
      }}
    >
      <div
        style={{
          width: "600px",
          height: "400px",
          border: "2px solid #ccc",
          borderRadius: "8px",
          overflow: "hidden",
          backgroundColor: "#fff",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <img
          src="https://upload.wikimedia.org/wikipedia/commons/9/96/Google_Maps_logo_2020.svg"
          alt="Google Maps Placeholder"
          style={{ maxWidth: "80%", maxHeight: "80%" }}
        />
      </div>
    </div>
  );
}

export default App;

