import { BrowserRouter, Routes, Route, Link, Navigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import ContainersPage from "./pages/ContainersPage";
import NodesPage from "./pages/NodesPage";
import JobsPage from "./pages/JobsPage";
import SettingsPage from "./pages/SettingsPage";

import logoLight from "./assets/logo-light.png";
import logoDark from "./assets/logo-dark.png";

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
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const isDark = localStorage.getItem('darkMode') === 'true';
    setDarkMode(isDark);

    // Listen for storage changes (when dark mode is toggled)
    const handleStorageChange = () => {
      const isDark = localStorage.getItem('darkMode') === 'true';
      setDarkMode(isDark);
    };

    window.addEventListener('storage', handleStorageChange);

    // Also listen for custom event from same window
    const handleDarkModeChange = () => {
      const isDark = localStorage.getItem('darkMode') === 'true';
      console.log('Dark mode changed to:', isDark);
      setDarkMode(isDark);
    };

    window.addEventListener('darkModeChange', handleDarkModeChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('darkModeChange', handleDarkModeChange);
    };
  }, []);

  return (
    <BrowserRouter>
      <header className="app-header">
        <nav className="app-header-nav-left">
          <NavItem to="/containers">Containers</NavItem>
          <NavItem to="/nodes">Nodes</NavItem>
        </nav>

        <div className="app-header-logo">
          <img
            src={darkMode ? logoDark : logoLight}
            alt="The Orchestrator"
            className="logo-image"
          />
        </div>

        <nav className="app-header-nav-right">
          <NavItem to="/jobs">Jobs</NavItem>
          <NavItem to="/settings">Settings</NavItem>
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/containers" replace />} />
          <Route path="/containers" element={<ContainersPage />} />
          <Route path="/nodes" element={<NodesPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}