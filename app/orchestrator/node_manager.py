# app/orchestrator/node_manager.py
import asyncio
from datetime import datetime
import httpx


class NodeManager:
    def __init__(self):
        self.nodes = {}
        self._monitor_task = None
        self._client = None

    async def _get_client(self):
        """Lazy initialize httpx client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=2.0)
        return self._client

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

    async def _refresh_node_status(self, node_id: str, node: dict):
        """
        Internal helper to check /health endpoint and update stats.
        """
        try:
            client = await self._get_client()
            url = f"http://{node['ip']}:{node['port']}/health"
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                node["status"] = "online"
                node["cpu_percent"] = data.get("cpu_percent", 0.0)
                node["memory_percent"] = data.get("memory_percent", 0.0)
                node["last_seen"] = datetime.utcnow().isoformat()
                return
        except Exception as e:
            pass
        # If it fails, mark offline
        node["status"] = "offline"
        node["cpu_percent"] = 0.0
        node["memory_percent"] = 0.0

    async def list_nodes_async(self):
        """
        Return all nodes, refreshing their /health status concurrently.
        """
        if not self.nodes:
            return self.nodes
        
        # Check all nodes concurrently
        tasks = []
        for node_id, node in list(self.nodes.items()):
            tasks.append(self._refresh_node_status(node_id, node))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        return self.nodes

    def list_nodes(self):
        """
        Synchronous version - returns nodes without refreshing status.
        Use list_nodes_async() for up-to-date status.
        """
        return self.nodes

    async def get_node_async(self, node_id: str):
        """Return single node with refreshed health info."""
        node = self.nodes.get(node_id)
        if not node:
            return None

        await self._refresh_node_status(node_id, node)
        return node

    def get_node(self, node_id: str):
        """Synchronous version - returns node without refreshing."""
        return self.nodes.get(node_id)

    def remove_node(self, node_id: str):
        """Remove a node by ID."""
        return self.nodes.pop(node_id, None)

    async def _monitor_nodes_loop(self):
        """
        Background async loop to periodically update node health.
        """
        while True:
            try:
                await self.list_nodes_async()
                await asyncio.sleep(5)  # every 5 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                await asyncio.sleep(5)

    def start_monitoring(self):
        """
        Start background monitoring (to run in FastAPI startup).
        """
        if not self._monitor_task or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self._monitor_nodes_loop())

    async def shutdown(self):
        """Cleanup resources"""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        if self._client:
            await self._client.aclose()