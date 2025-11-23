import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [form, setForm] = useState({ image: "python:3.11-slim", command: "" });
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const refresh = () => {
    setLoading(true);
    setErr(null);
    Promise.all([api.listJobs(), api.listNodes()])
      .then(([jobsData, nodesData]) => {
        setJobs(jobsData);
        setNodes(nodesData);
      })
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { refresh(); }, []);

  const onCreate = async (e) => {
    e.preventDefault();
    if (submitting) return; // Prevent double submission

    setErr(null);
    setSubmitting(true);

    // Check if any nodes are online
    const onlineNodes = nodes.filter(n => n.status === "online");
    if (onlineNodes.length === 0) {
      setErr("No online agents available. Please register and start at least one agent node first.");
      setSubmitting(false);
      return;
    }

    try {
      // Auto-generate unique job ID
      const jobId = `job-${Date.now()}`;
      await api.createJob({
        id: jobId,
        image: form.image,
        command: form.command || null,
        status: "pending"
      });
      setForm({ image: "python:3.11-slim", command: "" });
      refresh();
    } catch (e) {
      setErr(String(e.message || e));
    } finally {
      setSubmitting(false);
    }
  };

  const onDelete = async (id) => {
    setErr(null);
    try { await api.deleteJob(id); refresh(); }
    catch (e) { setErr(String(e.message || e)); }
  };

  const onlineNodes = nodes.filter(n => n.status === "online");

  return (
    <div className="page-container">
      <h2>Jobs</h2>

      {onlineNodes.length > 0 ? (
        <p style={{fontSize: '0.9em', color: '#28a745', marginBottom: '1rem'}}>
          ✓ {onlineNodes.length} agent{onlineNodes.length > 1 ? 's' : ''} online and ready
        </p>
      ) : (
        <p style={{fontSize: '0.9em', color: '#dc3545', marginBottom: '1rem'}}>
          ⚠ No agents online. Go to Nodes page to register agents first.
        </p>
      )}

      <form onSubmit={onCreate} className="form" style={{display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
        <input
          placeholder="Docker Image (e.g., python:3.11-slim, node:18, ubuntu)"
          value={form.image}
          onChange={(e) => setForm({ ...form, image: e.target.value })}
          className="input input-lg"
          required
        />
        <input
          placeholder="Command (e.g., python -c 'print(123)')"
          value={form.command}
          onChange={(e) => setForm({ ...form, command: e.target.value })}
          className="input input-lg"
        />
        <button type="submit" className="button" disabled={onlineNodes.length === 0 || submitting}>
          {submitting ? "Submitting..." : "Submit Job"}
        </button>
      </form>
      <p style={{fontSize: '0.85em', color: '#666', marginTop: '0.5rem'}}>
        Leave command empty to use image's default entrypoint
      </p>

      {err && <div className="error">{err}</div>}

      {loading ? (
        <div className="loading-text">Loading…</div>
      ) : (
        <div className="card-list">
          {jobs.map((j) => (
            <div key={j.id} className="card">
              <div className="card-info">
                <code className="card-id">{j.id}</code>
                <div className="card-main">{j.image}</div>
                {j.command && (
                  <div className="card-sub" style={{fontFamily: 'monospace', fontSize: '0.8em'}}>
                    $ {j.command}
                  </div>
                )}
                <div className="card-sub">
                  {j.status ?? "pending"} {j.node_id && `→ ${j.node_id}`}
                </div>
              </div>
              <button
                onClick={() => onDelete(j.id)}
                className="button button-danger button-sm"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}