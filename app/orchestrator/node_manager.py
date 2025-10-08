import requests
from datetime import datetime

class NodeManager:
    def __init__(self):
        self.nodes = {}

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
