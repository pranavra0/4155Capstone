from fastapi import APIRouter
from orchestrator.node_manager import NodeManager
from orchestrator.models import Node

router = APIRouter()
nm = NodeManager()

@router.post("/", response_model=Node)
def register_node(node: Node):
    nm.register_node(node.id, {"cpu": node.cpu, "memory": node.memory})
    return node

@router.get("/", response_model=list[Node])
def list_nodes():
    return [Node(id=nid, cpu=spec["cpu"], memory=spec["memory"]) for nid, spec in nm.list_nodes().items()]