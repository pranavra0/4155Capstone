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
    try { await api.createJob(form); setForm({ id: "", image: "", status: "pending" }); refresh(); }
    catch (e) { setErr(e.message); }
  };

  const onDelete = async (id) => {
    setErr(null);
    try { await api.deleteJob(id); refresh(); }
    catch (e) { setErr(e.message); }
  };

  return (
    <div style={{ padding: 16 }}>
      <h2>Jobs</h2>
      <form onSubmit={onCreate} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input placeholder="id" value={form.id} onChange={(e) => setForm({ ...form, id: e.target.value })} />
        <input placeholder="image" value={form.image} onChange={(e) => setForm({ ...form, image: e.target.value })} />
        <button>Submit</button>
      </form>

      {err && <div style={{ color: "crimson", marginBottom: 8 }}>{String(err)}</div>}
      {loading ? (
        <div>Loading…</div>
      ) : (
        <ul style={{ display: "grid", gap: 8 }}>
          {jobs.map((j) => (
            <li key={j.id} style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <code>{j.id}</code> — {j.image} — {j.status ?? "pending"}
              <button onClick={() => onDelete(j.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
