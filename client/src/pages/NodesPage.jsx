import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function NodesPage() {
  const [nodes, setNodes] = useState([]);
  const [form, setForm] = useState({ id: "node-1", ip: "127.0.0.1", port: 8001, cpu: 2, memory: 4096 });
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(false);

  const refresh = () => {
    setLoading(true);
    setErr(null);
    api.listNodes()
      .then(setNodes)
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, []);

  const setField = (k) => (e) =>
    setForm({
      ...form,
      [k]: ["port", "cpu", "memory"].includes(k) ? Number(e.target.value) : e.target.value,
    });

  const onCreate = async (e) => {
    e.preventDefault();
    setErr(null);
    try { await api.createNode(form); refresh(); }
    catch (e) { setErr(e.message); }
  };

  const onDelete = async (id) => {
    setErr(null);
    try { await api.deleteNode(id); refresh(); }
    catch (e) { setErr(e.message); }
  };

  return (
    // The inline style with the fontFamily override is now gone
    <div className="page-container">
      <h2>Nodes</h2>

      {/* This form uses the .form-grid class */}
      <form onSubmit={onCreate} className="form-grid">
        <input placeholder="ID" value={form.id} onChange={setField("id")} className="input" />
        <input placeholder="IP" value={form.ip} onChange={setField("ip")} className="input" />
        <input placeholder="Port" type="number" value={form.port} onChange={setField("port")} className="input" />
        <input placeholder="CPU" type="number" value={form.cpu} onChange={setField("cpu")} className="input" />
        <input placeholder="Memory" type="number" value={form.memory} onChange={setField("memory")} className="input" />
        <button type="submit" className="button">
          Add
        </button>
      </form>

      {err && <div className="error">{err}</div>}

      {loading ? (
        <div className="loading-text">Loading…</div>
      ) : (
        <div className="card-list">
          {nodes.map((n) => (
            <div key={n.id} className="card">
              <div className="card-info">
                <code className="card-id">{n.id}</code>
                <div className="card-main">{n.ip}:{n.port}</div>
                <div className="card-sub">CPU {n.cpu} — MEM {n.memory}</div>
              </div>
              <div className="card-status">{n.status ?? "unknown"}</div>
              <button
                onClick={() => onDelete(n.id)}
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