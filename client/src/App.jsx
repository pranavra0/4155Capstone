import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("http://localhost:8000/") 
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(() => setMessage("Failed to connect to backend"));
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", textAlign: "center", marginTop: "3rem" }}>
      <h1>React + FastAPI Orchestrator</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;