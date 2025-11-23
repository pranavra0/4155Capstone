// client/src/pages/ContainersPage.jsx
import { useEffect, useState, useRef } from "react";
import { api } from "../lib/api";

export default function ContainersPage() {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const initialLoad = useRef(true);

  const refresh = () => {
    if (!initialLoad.current) {
      setFetching(true);
    }
    setErr(null);
    api
      .listContainers(true)
      .then(setItems)
      .catch((e) => setErr(e.message))
      .finally(() => {
        setLoading(false);
        setFetching(false);
        initialLoad.current = false;
      });
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="page-container">
      <h2>Containers {fetching && <span style={{fontSize: '0.7em', color: '#888'}}>(refreshing...)</span>}</h2>
      <p style={{fontSize: '0.9em', color: '#666', marginBottom: '1rem'}}>
        Job containers running on agent nodes.
      </p>

      {err && <div className="error">{err}</div>}

      {loading ? (
        <div className="loading-text">Loading…</div>
      ) : (
        <div className="card-list">
          {items.length === 0 ? (
            <p style={{color: '#888'}}>No containers running</p>
          ) : (
            items.map((c, idx) => (
              <div key={`${c.node_id}-${c.id}-${idx}`} className="card">
                <div className="card-info">
                  <code className="card-id">{c.id?.slice(0, 12)}</code>
                  <div className="card-main">{c.name ?? "(no name)"}</div>
                  <div className="card-sub">{c.image ?? ""}</div>
                  <div className="card-sub" style={{color: '#007bff'}}>
                    Node: {c.node_id ?? "unknown"}
                  </div>
                </div>
                <div className="card-status">{c.status ?? ""}</div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}