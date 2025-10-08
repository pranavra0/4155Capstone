from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from orchestrator.node_manager import NodeManager
from orchestrator.models import Node

router = APIRouter()
nm = NodeManager()

class NodeUpdate(BaseModel):
    cpu: Optional[int] = None
    memory: Optional[int] = None

@router.post("/", response_model=Node)
def register_node(node: Node):
    nm.register_node(node.id, {"cpu": node.cpu, "memory": node.memory})
    return node

@router.get("/", response_model=list[Node])
def list_nodes():
    return [Node(id=nid, cpu=spec["cpu"], memory=spec["memory"]) for nid, spec in nm.list_nodes().items()]

@router.get("/{node_id}", response_model=Node)
def get_node(node_id: str):
    node = nm.get_node(node_id)
    if node is None:
        return {"error": f"Node {node_id} not found"}
    return Node(id=node_id, cpu=node["cpu"], memory=node["memory"])

@router.put("/{node_id}")
def update_node(node_id: str, update: NodeUpdate):
    updates = update.dict(exclude_none=True)
    updated = nm.update_node(node_id, updates)
    if updated is None:
        return {"error": f"Node {node_id} not found"}
    return {"id": node_id, **updated}