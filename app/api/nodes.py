# app/api/nodes.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter()


class NodeIn(BaseModel):
    id: str = Field(..., min_length=1)
    ip: str
    port: int
    cpu: int
    memory: int


def _serialize(node_id: str, node: dict) -> dict:
    return {
        "id": node_id,
        "ip": node.get("ip"),
        "port": node.get("port"),
        "cpu": node.get("cpu"),
        "memory": node.get("memory"),
        "status": node.get("status"),
        "last_seen": node.get("last_seen"),
        "cpu_percent": node.get("cpu_percent"),
        "memory_percent": node.get("memory_percent"),
        "heartbeat_failures": node.get("heartbeat_failures", 0),
        # diagnostics
        "last_http_code": node.get("last_http_code"),
        "last_error": node.get("last_error"),
    }


@router.get("/", summary="List nodes")
def list_nodes(request: Request):
    nm = request.app.state.nm
    nodes = nm.list_nodes()    # refreshes status internally
    return [_serialize(nid, n) for nid, n in nodes.items()]


@router.get("/{node_id}", summary="Get node")
def get_node(node_id: str, request: Request):
    nm = request.app.state.nm
    node = nm.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return _serialize(node_id, node)


@router.post("/", summary="Register/Update node")
def register_node(body: NodeIn, request: Request):
    nm = request.app.state.nm
    nm.register_node(body.id, {
        "ip": body.ip,
        "port": body.port,
        "cpu": body.cpu,
        "memory": body.memory,
    })
    node = nm.get_node(body.id)
    return _serialize(body.id, node)


@router.post("/{node_id}/ping", summary="Force a heartbeat refresh and return diagnostics")
def ping_node(node_id: str, request: Request):
    nm = request.app.state.nm
    node = nm.nodes.get(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    nm._refresh_node_status(node_id, node, reason="manual-ping")
    return _serialize(node_id, node)


@router.delete("/{node_id}", summary="Remove node")
def delete_node(node_id: str, request: Request):
    nm = request.app.state.nm
    removed = nm.remove_node(node_id)
    if removed is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"status": "removed", "id": node_id}
