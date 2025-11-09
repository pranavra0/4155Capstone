import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [form, setForm] = useState({ id: "job-1", image: "alpine:latest", status: "pending" });
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(false);

  const refresh = () => {
    setLoading(true);
    setErr(null);
    api.listJobs()
      .then(setJobs)
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { refresh(); }, []);

  const onCreate = async (e) => {
    e.preventDefault();
    setErr(null);
    try {
      await api.createJob(form);
      setForm({ id: "", image: "", status: "pending" });
      refresh();
    } catch (e) {
      setErr(String(e.message || e));
    }
  };

  const onDelete = async (id) => {
    setErr(null);
    try { await api.deleteJob(id); refresh(); }
    catch (e) { setErr(String(e.message || e)); }
  };

  return (
    <div className="page-container">
      <h2>Jobs</h2>

      <form onSubmit={onCreate} className="form">
        <input
          placeholder="Job ID"
          value={form.id}
          onChange={(e) => setForm({ ...form, id: e.target.value })}
          className="input"
        />
        <input
          placeholder="Image"
          value={form.image}
          onChange={(e) => setForm({ ...form, image: e.target.value })}
          className="input input-lg"
        />
        <button type="submit" className="button">
          Submit
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
                <div className="card-sub">{j.status ?? "pending"}</div>
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