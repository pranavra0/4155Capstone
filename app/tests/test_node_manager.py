import asyncio
from typing import Any, Dict

from orchestrator.node_manager import NodeManager


def make_manager() -> NodeManager:
    """Create a fresh NodeManager and clear any nodes loaded from the DB."""
    m = NodeManager()
    m.nodes.clear()
    return m


def test_register_node_updates_in_memory_only():
    manager = make_manager()
    info = {
        "ip": "127.0.0.1",
        "port": 8001,
        "cpu": 4,
        "memory": 8192,
    }

    manager.register_node("node1", info)

    # In-memory state is updated
    assert "node1" in manager.nodes
    node = manager.nodes["node1"]
    assert node["ip"] == info["ip"]
    assert node["port"] == info["port"]
    assert node["cpu"] == info["cpu"]
    assert node["memory"] == info["memory"]

    # Default runtime fields
    assert node["status"] == "unknown"
    assert node["cpu_percent"] is None
    assert node["memory_percent"] is None
    assert node["last_seen"] is None


def test_remove_node_removes_from_nodes_dict():
    manager = make_manager()
    # Seed a node
    manager.nodes["node1"] = {
        "ip": "127.0.0.1",
        "port": 8001,
        "cpu": 4,
        "memory": 8192,
        "status": "online",
        "cpu_percent": 10.0,
        "memory_percent": 20.0,
        "last_seen": None,
    }

    removed = manager.remove_node("node1")

    # Node is returned and removed from the dict
    assert removed is not None
    assert "node1" not in manager.nodes


def test_list_nodes_async_calls_refresh(monkeypatch):
    manager = make_manager()
    manager.nodes["node1"] = {
        "ip": "127.0.0.1",
        "port": 8001,
        "cpu": 4,
        "memory": 8192,
        "status": "unknown",
        "cpu_percent": 0.0,
        "memory_percent": 0.0,
        "last_seen": None,
    }

    async def fake_refresh(node_id: str, node: Dict[str, Any]):
        # Simulate a successful health check
        node["status"] = "online"
        node["cpu_percent"] = 15.0
        node["memory_percent"] = 30.0

    # Patch the instance method so no real HTTP is done
    monkeypatch.setattr(manager, "_refresh_node_status", fake_refresh)

    # Drive the async API without pytest-asyncio
    result = asyncio.run(manager.list_nodes_async())

    assert result["node1"]["status"] == "online"
    assert result["node1"]["cpu_percent"] == 15.0
    assert result["node1"]["memory_percent"] == 30.0
