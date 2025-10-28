# app/orchestrator/node_manager.py
import requests
import asyncio
import logging
from datetime import datetime, timedelta

log = logging.getLogger("orchestrator.node_heartbeat")


class NodeManager:
    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self._monitor_task: asyncio.Task | None = None
        log.debug("NodeManager initialized")

    def register_node(self, node_id: str, info: dict):
        """
        Register a new node with info:
        Example: {"ip": "127.0.0.1", "port": 8001, "cpu": 4, "memory": 8192}
        """
        self.nodes[node_id] = {
            "ip": info["ip"],
            "port": int(info["port"]),
            "cpu": int(info["cpu"]),
            "memory": int(info["memory"]),
            "status": "unknown",
            "cpu_percent": None,
            "memory_percent": None,
            "last_seen": None,
            "heartbeat_failures": 0,
            # --- new diagnostics ---
            "last_http_code": None,
            "last_error": None,
        }
        log.info(
            "Registered node %s at %s:%s (cpu=%s, mem=%s)",
            node_id, info["ip"], info["port"], info["cpu"], info["memory"]
        )
        # Immediate refresh so status flips right away if reachable
        try:
            self._refresh_node_status(node_id, self.nodes[node_id], reason="register")
        except Exception as e:
            log.debug("Immediate refresh failed for %s: %s", node_id, e)

    def list_nodes(self):
        """Return all nodes, refreshing their /health status."""
        for node_id, node in list(self.nodes.items()):
            self._refresh_node_status(node_id, node, reason="list")
        return self.nodes

    def get_node(self, node_id: str):
        """Return single node (with most recent health info if reachable)."""
        node = self.nodes.get(node_id)
        if not node:
            return None
        self._refresh_node_status(node_id, node, reason="get")
        return node

    def remove_node(self, node_id: str):
        """Remove a node by ID."""
        removed = self.nodes.pop(node_id, None)
        if removed is not None:
            log.info("Deregistered node %s", node_id)
        else:
            log.warning("Attempted to deregister missing node %s", node_id)
        return removed

    # ---------------- internal ----------------

    def _refresh_node_status(self, node_id: str, node: dict, reason: str = "loop"):
        """
        Check /health and update stats. Logs transitions (online/offline)
        and basic heartbeat info. `reason` is for debugging (loop/list/get/register).
        Adds a 10s grace window to avoid flapping to OFFLINE on brief hiccups.
        Records last_http_code and last_error for diagnostics.
        """
        prev_status = node.get("status", "unknown")
        url = f"http://{node['ip']}:{node['port']}/health"

        node["last_http_code"] = None
        node["last_error"] = None

        try:
            resp = requests.get(url, timeout=3.0)
            code = resp.status_code
            node["last_http_code"] = code
            log.info("Heartbeat %s %s → %s (reason=%s, prev=%s)", node_id, url, code, reason, prev_status)

            if 200 <= code < 300:
                cpu_p = 0.0
                mem_p = 0.0
                try:
                    data = resp.json()
                    cpu_p = float(data.get("cpu_percent", 0.0) or 0.0)
                    mem_p = float(data.get("memory_percent", 0.0) or 0.0)
                except Exception as e:
                    node["last_error"] = f"json_parse: {e}"
                    # Still online even if parsing fails
                    log.info("Heartbeat %s JSON parse issue: %s (treated as online)", node_id, e)

                node["status"] = "online"
                node["cpu_percent"] = cpu_p
                node["memory_percent"] = mem_p
                node["last_seen"] = datetime.utcnow().isoformat()
                node["heartbeat_failures"] = 0

                if prev_status != "online":
                    log.info(
                        "Node %s ONLINE %s:%s cpu=%.1f%% mem=%.1f%% (reason=%s, code=%s)",
                        node_id, node["ip"], node["port"], cpu_p, mem_p, reason, code
                    )
                else:
                    log.debug(
                        "Heartbeat ok: %s cpu=%.1f%% mem=%.1f%% (reason=%s, code=%s)",
                        node_id, cpu_p, mem_p, reason, code
                    )
                return  # success path
            else:
                node["last_error"] = f"non_2xx:{code}"
                log.info("Heartbeat %s non-2xx (%s) body=%s", node_id, code, resp.text[:200])

        except Exception as e:
            node["last_error"] = f"request_error:{e}"
            log.info("Heartbeat %s error: %s", node_id, e)

        # Failure path: apply a 10s grace window if we were recently online
        last_seen = node.get("last_seen")
        if last_seen:
            try:
                seen_dt = datetime.fromisoformat(last_seen)
                if datetime.utcnow() - seen_dt <= timedelta(seconds=10):
                    node["heartbeat_failures"] = (node.get("heartbeat_failures") or 0) + 1
                    log.info(
                        "Heartbeat %s transient failure kept ONLINE (failures=%s, reason=%s)",
                        node_id, node["heartbeat_failures"], reason
                    )
                    return
            except Exception:
                pass  # if parsing fails, fall through to offline

        # Flip to offline
        node["status"] = "offline"
        node["cpu_percent"] = 0.0
        node["memory_percent"] = 0.0
        node["heartbeat_failures"] = (node.get("heartbeat_failures") or 0) + 1

        if prev_status != "offline":
            log.warning(
                "Node %s OFFLINE (last_seen=%s, failures=%s, reason=%s)",
                node_id, node.get("last_seen"), node["heartbeat_failures"], reason
            )
        else:
            log.info(
                "Heartbeat %s still OFFLINE (failures=%s, reason=%s)",
                node_id, node["heartbeat_failures"], reason
            )

    async def _monitor_nodes_loop(self):
        """Background async loop to periodically update node health."""
        log.info("Starting node heartbeat monitor loop (interval=5s)")
        while True:
            for node_id, node in list(self.nodes.items()):
                self._refresh_node_status(node_id, node, reason="loop")
            await asyncio.sleep(5)

    def start_monitoring(self):
        """Start background monitoring (to run in FastAPI startup)."""
        if not self._monitor_task:
            self._monitor_task = asyncio.create_task(self._monitor_nodes_loop())
            log.info("Node heartbeat monitoring started")
        else:
            log.debug("Node heartbeat monitoring already running")
