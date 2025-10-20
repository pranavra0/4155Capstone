import requests
import asyncio
from datetime import datetime

class NodeManager:
    def __init__(self):
        self.nodes = {}
        self._monitor_task = None

    def register_node(self, node_id: str, info: dict):
        """
        Register a new node with info:
        Example: {"ip": "127.0.0.1", "port": 8001, "cpu": 4, "memory": 8192}
        """
        self.nodes[node_id] = {
            "ip": info["ip"],
            "port": info["port"],
            "cpu": info["cpu"],
            "memory": info["memory"],
            "status": "unknown",
            "cpu_percent": None,
            "memory_percent": None,
            "last_seen": None,
        }

    def list_nodes(self):
        """
        Return all nodes, refreshing their /health status.
        """
        for node_id, node in list(self.nodes.items()):
            try:
                url = f"http://{node['ip']}:{node['port']}/health"
                resp = requests.get(url, timeout=1)
                if resp.status_code == 200:
                    data = resp.json()
                    node["status"] = "online"
                    node["cpu_percent"] = data.get("cpu_percent")
                    node["memory_percent"] = data.get("memory_percent")
                    node["last_seen"] = datetime.utcnow().isoformat()
                else:
                    node["status"] = "offline"
            except Exception:
                node["status"] = "offline"
        return self.nodes

    def get_node(self, node_id: str):
        """Return single node (with most recent health info if reachable)."""
        node = self.nodes.get(node_id)
        if not node:
            return None

        try:
            url = f"http://{node['ip']}:{node['port']}/health"
            resp = requests.get(url, timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                node["status"] = "online"
                node["cpu_percent"] = data.get("cpu_percent")
                node["memory_percent"] = data.get("memory_percent")
                node["last_seen"] = datetime.utcnow().isoformat()
        except Exception:
            node["status"] = "offline"
        return node

    def remove_node(self, node_id: str):
        """Remove a node by ID."""
        return self.nodes.pop(node_id, None)

    def _refresh_node_status(self, node_id: str, node: dict):
        """
        Internal helper to check /health endpoint and update stats.
        """
        try:
            url = f"http://{node['ip']}:{node['port']}/health"
            resp = requests.get(url, timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                node["status"] = "online"
                node["cpu_percent"] = data.get("cpu_percent", 0.0)
                node["memory_percent"] = data.get("memory_percent", 0.0)
                node["last_seen"] = datetime.utcnow().isoformat()
                return
        except Exception:
            pass
        # If it fails, mark offline
        node["status"] = "offline"
        node["cpu_percent"] = 0.0
        node["memory_percent"] = 0.0

    async def _monitor_nodes_loop(self):
        """
        Background async loop to periodically update node health.
        """
        while True:
            for node_id, node in list(self.nodes.items()):
                self._refresh_node_status(node_id, node)
            await asyncio.sleep(5)  # every 5 seconds

    def start_monitoring(self):
        """
        Start background monitoring (to run in FastAPI startup).
        """
        if not self._monitor_task:
            self._monitor_task = asyncio.create_task(self._monitor_nodes_loop())
