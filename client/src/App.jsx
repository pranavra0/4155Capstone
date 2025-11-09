import { BrowserRouter, Routes, Route, Link, Navigate, useLocation } from "react-router-dom";
import ContainersPage from "./pages/ContainersPage";
import NodesPage from "./pages/NodesPage";
import JobsPage from "./pages/JobsPage";

// Import the stylesheet (if not already imported in index.js or main.jsx)
import "./index.css";

function NavItem({ to, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  const className = `nav-item ${isActive ? "active" : ""}`;

  return (
    <Link to={to} className={className}>
      {children}
    </Link>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <header className="app-header">
        <h1 className="app-header-title">
          The Orchestrator
        </h1>
        <nav className="app-header-nav">
          <NavItem to="/containers">Containers</NavItem>
          <NavItem to="/nodes">Nodes</NavItem>
          <NavItem to="/jobs">Jobs</NavItem>
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/containers" replace />} />
          <Route path="/containers" element={<ContainersPage />} />
          <Route path="/nodes" element={<NodesPage />} />
          <Route path="/jobs" element={<JobsPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}