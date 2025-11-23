import { useEffect, useState, useRef } from "react";
import { api } from "../lib/api";

export default function NodesPage() {
  const [nodes, setNodes] = useState([]);
  const [form, setForm] = useState({ id: "", ip: "", port: 8001, cpu: "", memory: "" });
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const formTouched = useRef(false);
  const initialLoad = useRef(true);

  const refresh = () => {
    // Don't show loading spinner on subsequent refreshes (prevents flickering)
    if (!initialLoad.current) {
      setFetching(true);
    }

    api.listNodes()
      .then((nodesData) => {
        setNodes(nodesData);

        // Only auto-fill form if user hasn't touched it yet
        if (!formTouched.current) {
          if (nodesData.length > 0) {
            const nextNodeNum = nodesData.length + 1;
            const lastNode = nodesData[nodesData.length - 1];
            const nextPort = Math.max(...nodesData.map(n => n.port)) + 1;

            setForm(prev => ({
              ...prev,
              id: `node-${nextNodeNum}`,
              ip: lastNode.ip || "",
              port: nextPort
            }));
          } else {
            setForm(prev => ({
              ...prev,
              id: "node-1",
              port: 8001
            }));
          }
        }
      })
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

  const setField = (k) => (e) => {
    formTouched.current = true;
    setForm({
      ...form,
      [k]: ["port", "cpu", "memory"].includes(k) ? Number(e.target.value) : e.target.value,
    });
  };

  // Auto-detect CPU and memory from agent
  const autoDetect = async () => {
    if (!form.ip || !form.port) {
      setErr("Enter IP and Port first");
      return;
    }
    setErr(null);
    try {
      const response = await fetch(`http://${form.ip}:${form.port}/health`);
      if (!response.ok) throw new Error("Agent not reachable");
      const data = await response.json();
      setForm(prev => ({
        ...prev,
        cpu: data.cpu_count || prev.cpu,
        memory: data.memory_total_mb || prev.memory
      }));
    } catch (e) {
      setErr("Could not reach agent: " + e.message);
    }
  };

  const onCreate = async (e) => {
    e.preventDefault();
    setErr(null);
    try {
      await api.createNode(form);
      formTouched.current = false;
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
    <div className="page-container">
      <h2>Nodes {fetching && <span style={{fontSize: '0.7em', color: '#888'}}>(refreshing...)</span>}</h2>

      {/* This form uses the .form-grid class */}
      <form onSubmit={onCreate} className="form-grid">
        <input placeholder="Node ID" value={form.id} onChange={setField("id")} className="input" required />
        <input placeholder="IP Address" value={form.ip} onChange={setField("ip")} className="input" required />
        <input placeholder="Port" type="number" value={form.port} onChange={setField("port")} className="input" required />
        <input placeholder="CPU Cores" type="number" value={form.cpu} onChange={setField("cpu")} className="input" required />
        <input placeholder="Memory (MB)" type="number" value={form.memory} onChange={setField("memory")} className="input" required />
        <button type="button" onClick={autoDetect} className="button" style={{backgroundColor: '#666'}}>
          Auto-detect
        </button>
        <button type="submit" className="button">
          Register Node
        </button>
      </form>
      <p style={{fontSize: '0.9em', color: '#666', marginTop: '0.5rem'}}>
        Enter IP and Port, then click "Auto-detect" to fill CPU/Memory from the agent.
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
                <div className="card-sub">CPU {n.cpu} — MEM {n.memory} MB</div>
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