import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function SettingsPage() {
  const [settings, setSettings] = useState(null);
  const [selectedStrategy, setSelectedStrategy] = useState("");
  const [err, setErr] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
    if (savedDarkMode) {
      document.documentElement.classList.add('dark-mode');
    }
  }, []);

  const refresh = () => {
    setLoading(true);
    setErr(null);
    api.getSchedulerSettings()
      .then((data) => {
        setSettings(data);
        setSelectedStrategy(data.strategy);
      })
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { refresh(); }, []);

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode);
    if (newDarkMode) {
      document.documentElement.classList.add('dark-mode');
    } else {
      document.documentElement.classList.remove('dark-mode');
    }
    // Dispatch custom event so App.jsx can update the logo
    window.dispatchEvent(new Event('darkModeChange'));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr(null);
    setSuccess(null);
    try {
      const result = await api.updateSchedulerSettings({ strategy: selectedStrategy });
      setSuccess(result.message);
      refresh();
    } catch (e) {
      setErr(e.message);
    }
  };

  const strategyDescriptions = {
    first_fit: "Always assigns jobs to the first available node. Simple and fast.",
    round_robin: "Distributes jobs evenly across all nodes in rotation. Best for balanced load distribution.",
    resource_aware: "Assigns jobs to the node with the lowest CPU usage. Optimizes resource utilization."
  };

  return (
    <div className="page-container">
      <h2>Settings</h2>

      {loading ? (
        <div className="loading-text">Loading…</div>
      ) : (
        <>
          <h3 style={{marginTop: '2rem', marginBottom: '1rem'}}>Appearance</h3>
          <div style={{marginBottom: '2rem'}}>
            <label style={{display: 'flex', alignItems: 'center', cursor: 'pointer', width: 'fit-content'}}>
              <input
                type="checkbox"
                checked={darkMode}
                onChange={toggleDarkMode}
                style={{marginRight: '0.5rem', width: '18px', height: '18px', cursor: 'pointer'}}
              />
              <span style={{fontSize: '16px'}}>Dark Mode</span>
            </label>
          </div>

          <h3 style={{marginTop: '2rem', marginBottom: '1rem'}}>Scheduling Strategy</h3>

          {settings && (
            <form onSubmit={onSubmit}>
              <div style={{display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '600px'}}>
                {settings.available_strategies.map(strategy => (
                  <label
                    key={strategy}
                    className="card"
                    style={{
                      border: '2px solid',
                      borderColor: selectedStrategy === strategy ? '#1a73e8' : 'var(--border-color)',
                      cursor: 'pointer',
                      background: selectedStrategy === strategy ? 'rgba(26, 115, 232, 0.1)' : 'var(--bg-secondary)'
                    }}
                  >
                    <input
                      type="radio"
                      name="strategy"
                      value={strategy}
                      checked={selectedStrategy === strategy}
                      onChange={(e) => setSelectedStrategy(e.target.value)}
                      style={{marginRight: '1rem', marginTop: '0.2rem', cursor: 'pointer'}}
                    />
                    <div style={{flex: 1}}>
                      <div style={{fontWeight: 'bold', marginBottom: '0.25rem'}}>
                        {strategy.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                      </div>
                      <div style={{fontSize: '0.9em', color: 'var(--text-secondary)'}}>
                        {strategyDescriptions[strategy]}
                      </div>
                    </div>
                  </label>
                ))}
              </div>

              <button
                type="submit"
                className="button"
                style={{marginTop: '1.5rem'}}
                disabled={selectedStrategy === settings.strategy}
              >
                Update Strategy
              </button>
            </form>
          )}

          {success && <div style={{marginTop: '1rem', padding: '1rem', background: '#d4edda', color: '#155724', borderRadius: '4px'}}>{success}</div>}
          {err && <div className="error" style={{marginTop: '1rem'}}>{err}</div>}
        </>
      )}
    </div>
  );
}
