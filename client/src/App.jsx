import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import ContainersPage from "./pages/ContainersPage";
import NodesPage from "./pages/NodesPage";
import JobsPage from "./pages/JobsPage";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ display: "flex", gap: 12, padding: 16, borderBottom: "1px solid #ddd" }}>
        <Link to="/containers">Containers</Link>
        <Link to="/nodes">Nodes</Link>
        <Link to="/jobs">Jobs</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Navigate to="/containers" replace />} />
        <Route path="/containers" element={<ContainersPage />} />
        <Route path="/nodes" element={<NodesPage />} />
        <Route path="/jobs" element={<JobsPage />} />
      </Routes>
    </BrowserRouter>
  );
}
