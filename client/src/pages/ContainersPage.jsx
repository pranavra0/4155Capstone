// client/src/pages/ContainersPage.jsx
import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function ContainersPage() {
  const [items, setItems] = useState([]);
  const [image, setImage] = useState("nginx:latest");
  const [name, setName] = useState("web-1");
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(false);

  const refresh = () => {
    setLoading(true);
    setErr(null);
    // list only running containers to avoid exited clutter
    api
      .listContainers(false)
      .then(setItems)
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    refresh();
  }, []);

  const onCreate = async (e) => {
    e.preventDefault();
    setErr(null);
    try {
      await api.createContainer({ image, name });
      refresh();
    } catch (e) {
      setErr(String(e.message || e));
    }
  };

  const onDelete = async (id) => {
    setErr(null);
    try {
      await api.deleteContainer(id);
      refresh();
    } catch (e) {
      setErr(String(e.message || e));
    }
  };

  return (
    <div style={{ padding: 16 }}>
      <h2>Containers</h2>

      <form onSubmit={onCreate} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          value={image}
          onChange={(e) => setImage(e.target.value)}
          placeholder="image (e.g. nginx:latest)"
        />
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="name (optional)" />
        <button type="submit">Start</button>
      </form>

      {err && <div style={{ color: "crimson", marginBottom: 8 }}>{err}</div>}

      {loading ? (
        <div>Loading…</div>
      ) : (
        <ul style={{ display: "grid", gap: 8 }}>
          {items.map((c) => (
            <li key={c.id} style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <code>{c.id?.slice(0, 12) ?? ""}</code>
              <span>{c.name ?? "(no name)"}</span>
              <span>{c.image ?? ""}</span>
              <span style={{ opacity: 0.7 }}>{c.status ?? ""}</span>
              <button onClick={() => onDelete(c.id)}>Stop/Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
