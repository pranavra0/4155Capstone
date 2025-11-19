import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function NodesPage() {
  const [nodes, setNodes] = useState([]);
  const [form, setForm] = useState({ id: "", ip: "127.0.0.1", port: 8001, cpu: 4, memory: 8192 });
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(false);

  const refresh = () => {
    setLoading(true);
    setErr(null);
    api.listNodes()
      .then((nodesData) => {
        setNodes(nodesData);

        // Auto-generate next node ID and port
        if (nodesData.length > 0) {
          const nextNodeNum = nodesData.length + 1;
          const lastNode = nodesData[nodesData.length - 1];
          const nextPort = Math.max(...nodesData.map(n => n.port)) + 1;

          setForm(prev => ({
            ...prev,
            id: `node-${nextNodeNum}`,
            ip: lastNode.ip || "127.0.0.1",
            port: nextPort
          }));
        } else {
          setForm(prev => ({
            ...prev,
            id: "node-1",
            ip: "127.0.0.1",
            port: 8001
          }));
        }
      })
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
    try {
      await api.createNode(form);
      refresh();
    }
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
        <input placeholder="Node ID" value={form.id} onChange={setField("id")} className="input" required />
        <input placeholder="IP Address" value={form.ip} onChange={setField("ip")} className="input" required />
        <input placeholder="Port" type="number" value={form.port} onChange={setField("port")} className="input" required />
        <input placeholder="CPU Cores" type="number" value={form.cpu} onChange={setField("cpu")} className="input" required />
        <input placeholder="Memory (MB)" type="number" value={form.memory} onChange={setField("memory")} className="input" required />
        <button type="submit" className="button">
          Register Node
        </button>
      </form>
      <p style={{fontSize: '0.9em', color: '#666', marginTop: '0.5rem'}}>
        Fields auto-fill based on existing nodes. You can modify them before registering.
      </p>

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