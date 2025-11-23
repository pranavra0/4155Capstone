import { useEffect, useState } from "react";
import { api } from "../lib/api";

const ALLOWED_IMAGES = [
  'python:3.11-slim', 'python:3.10-slim', 'python:3.9-slim',
  'node:20-slim', 'node:18-slim',
  'ruby:3.2-slim', 'golang:1.21-alpine', 'rust:slim',
  'ubuntu:22.04', 'debian:bookworm-slim', 'alpine:3.18',
  'nginx:alpine', 'redis:alpine', 'postgres:15-alpine',
  'openjdk:17-slim', 'maven:3.9-eclipse-temurin-17',
];

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [form, setForm] = useState({ image: ALLOWED_IMAGES[0], command: "" });
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
      setForm({ image: ALLOWED_IMAGES[0], command: "" });
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

      <form onSubmit={onCreate} className="form-grid" style={{gridTemplateColumns: '1fr 1fr auto'}}>
        <select
          value={form.image}
          onChange={(e) => setForm({ ...form, image: e.target.value })}
          className="input"
          required
        >
          {ALLOWED_IMAGES.map(img => (
            <option key={img} value={img}>{img}</option>
          ))}
        </select>
        <input
          placeholder="Command (optional)"
          value={form.command}
          onChange={(e) => setForm({ ...form, command: e.target.value })}
          className="input"
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