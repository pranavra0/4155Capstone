import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [form, setForm] = useState({ image: "nginx" });
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
      await api.createJob({ id: jobId, image: form.image, status: "pending" });
      setForm({ image: "" });
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

      <form onSubmit={onCreate} className="form">
        <input
          placeholder="Docker Image (e.g., nginx, redis, mongo)"
          value={form.image}
          onChange={(e) => setForm({ ...form, image: e.target.value })}
          className="input input-lg"
          required
        />
        <button type="submit" className="button" disabled={onlineNodes.length === 0 || submitting}>
          {submitting ? "Submitting..." : "Submit Job"}
        </button>
      </form>

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