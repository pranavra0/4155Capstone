# app/api/nodes.py
from fastapi import APIRouter, HTTPException
from orchestrator.models import Node
from orchestrator import node_manager

router = APIRouter()


@router.post("/", response_model=Node)
@router.post("", response_model=Node)
def register_node(node: Node):
    """Register a new node"""
    node_manager.register_node(node.id, {
        "ip": node.ip,
        "port": node.port,
        "cpu": node.cpu,
        "memory": node.memory
    })
    return node


@router.get("/", response_model=list[Node])
@router.get("", response_model=list[Node])
async def list_nodes():
    """List all nodes with current health status"""
    nodes_dict = await node_manager.list_nodes_async()
    nodes = []
    for nid, spec in nodes_dict.items():
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


@router.get("/{node_id}", response_model=Node)
async def get_node(node_id: str):
    """Get single node with refreshed health"""
    node_data = await node_manager.get_node_async(node_id)
    if node_data is None:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return Node(
        id=node_id,
        ip=node_data["ip"],
        port=node_data["port"],
        cpu=node_data["cpu"],
        memory=node_data["memory"],
        status=node_data.get("status", "unknown"),
        last_seen=node_data.get("last_seen"),
        cpu_percent=node_data.get("cpu_percent", 0),
        memory_percent=node_data.get("memory_percent", 0)
    )


@router.delete("/{node_id}")
def deregister_node(node_id: str):
    """Deregister a node"""
    deleted = node_manager.remove_node(node_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"status": "deleted", "id": node_id}