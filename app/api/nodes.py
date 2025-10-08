from fastapi import APIRouter
from orchestrator.node_manager import NodeManager
from orchestrator.models import Node

router = APIRouter()
nm = NodeManager()

@router.post("/", response_model=Node)
def register_node(node: Node):
    nm.register_node(node.id, {
    "ip": node.ip,
    "port": node.port,
    "cpu": node.cpu,
    "memory": node.memory
    })
    return node

@router.get("/", response_model=list[Node])
def list_nodes():
    nodes = []
    for nid, spec in nm.list_nodes().items():
        nodes.append(Node(
            id=nid,
            ip=spec["ip"],
            port=spec["port"],
            cpu=spec["cpu"],
            memory=spec["memory"],
            status=spec.get("status", "unknown"),
            last_seen=spec.get("last_seen"),
            cpu_percent=spec.get("cpu_percent", 0),
            memory_percent=spec.get("memory_percent", 0)
        ))
    return nodes