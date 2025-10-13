// src/lib/api.js
const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function http(path, init) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    credentials: "include",
    ...init,
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(txt || `HTTP ${res.status}`);
  }
  return res.status === 204 ? undefined : await res.json();
}

export const api = {
  // ========= CONTAINERS (query params per Swagger) =========
  listContainers: (all = true) => http(`/containers?all=${all}`),

  createContainer: ({ image, name }) =>
    http(
      `/containers?image=${encodeURIComponent(image)}&name=${encodeURIComponent(name)}`,
      { method: "POST" }
    ),

  deleteContainer: (id) => http(`/containers/${id}`, { method: "DELETE" }),

  // ========= NODES (JSON body) =========
  listNodes: () => http(`/nodes`),

  createNode: ({ id, ip, port, cpu, memory }) =>
    http(`/nodes`, {
      method: "POST",
      body: JSON.stringify({ id, ip, port, cpu, memory }),
    }),

  deleteNode: (id) => http(`/nodes/${id}`, { method: "DELETE" }),

  // ========= JOBS (JSON body) =========
  listJobs: () => http(`/jobs`),

  createJob: ({ id, image, status = "pending" }) =>
    http(`/jobs`, {
      method: "POST",
      body: JSON.stringify({ id, image, status }),
    }),

  deleteJob: (id) => http(`/jobs/${id}`, { method: "DELETE" }),
};
