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
    <div className="page-container">
      <h2>Containers</h2>

      <form onSubmit={onCreate} className="form">
        <input
          value={image}
          onChange={(e) => setImage(e.target.value)}
          placeholder="Image (e.g. nginx:latest)"
          className="input input-lg"
        />
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Name (optional)"
          className="input"
        />
        <button type="submit" className="button">
          Start
        </button>
      </form>

      {err && <div className="error">{err}</div>}

      {loading ? (
        <div className="loading-text">Loading…</div>
      ) : (
        <div className="card-list">
          {items.map((c) => (
            <div key={c.id} className="card">
              <div className="card-info">
                <code className="card-id">{c.id?.slice(0, 12)}</code>
                <div className="card-main">{c.name ?? "(no name)"}</div>
                <div className="card-sub">{c.image ?? ""}</div>
              </div>
              <div className="card-status">{c.status ?? ""}</div>
              <button
                onClick={() => onDelete(c.id)}
                className="button button-danger button-sm"
              >
                Stop/Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}