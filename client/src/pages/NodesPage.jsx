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
    // Auto-refresh every 5 seconds to show node status changes
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, []);

  const set = (k) => (e) =>
    setForm({ ...form, [k]: ["port", "cpu", "memory"].includes(k) ? Number(e.target.value) : e.target.value });

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
    <div style={{ padding: 16 }}>
      <h2>Nodes</h2>
      <form onSubmit={onCreate} style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr) auto", gap: 8, marginBottom: 16 }}>
        <input placeholder="id" value={form.id} onChange={set("id")} />
        <input placeholder="ip" value={form.ip} onChange={set("ip")} />
        <input placeholder="port" type="number" value={form.port} onChange={set("port")} />
        <input placeholder="cpu" type="number" value={form.cpu} onChange={set("cpu")} />
        <input placeholder="memory" type="number" value={form.memory} onChange={set("memory")} />
        <button>Add</button>
      </form>

      {err && <div style={{ color: "crimson", marginBottom: 8 }}>{String(err)}</div>}
      {loading ? (
        <div>Loading…</div>
      ) : (
        <ul style={{ display: "grid", gap: 8 }}>
          {nodes.map((n) => (
            <li key={n.id} style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <code>{n.id}</code> — {n.ip}:{n.port} — CPU {n.cpu} — MEM {n.memory} — {n.status ?? "unknown"}
              <button onClick={() => onDelete(n.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
