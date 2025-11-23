# app/api/containers.py
from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, Query
from docker.errors import APIError, NotFound

from orchestrator.container_manager import DockerUnavailable
from orchestrator import container_manager
from database import get_collection

router = APIRouter()


def _serialize(c, node_id: str = None) -> dict:
    """Convert a Docker SDK Container to a small, FE-friendly dict."""
    name = None
    try:
        name = getattr(c, "name", None)
        if not name:
            c.reload()
            name = (c.attrs.get("Name", "") or "").lstrip("/")
    except Exception:
        name = None

    image = "<none>"
    try:
        tags = getattr(c.image, "tags", None)
        if tags:
            image = tags[0]
    except Exception:
        pass

    status = None
    try:
        status = getattr(c, "status", None)
    except Exception:
        pass

    result = {"id": c.id, "name": name, "image": image, "status": status}
    if node_id:
        result["node_id"] = node_id
    return result


@router.get("/", summary="List Containers")
@router.get("", summary="List Containers")
async def list_containers(all: bool = Query(True, description="Include stopped/exited containers")):
    all_containers = []

    # Get local orchestrator containers
    try:
        local_items = await container_manager.list_containers_async(all=all)
        for c in local_items:
            container = _serialize(c, node_id="orchestrator")
            all_containers.append(container)
    except DockerUnavailable:
        pass

    # Get containers from all registered nodes
    nodes = list(get_collection("nodes").find())
    async with httpx.AsyncClient(timeout=5.0) as client:
        for node in nodes:
            try:
                url = f"http://{node['ip']}:{node['port']}/containers?all={str(all).lower()}"
                resp = await client.get(url)
                if resp.status_code == 200:
                    containers = resp.json()
                    for c in containers:
                        c["node_id"] = node["id"]
                        all_containers.append(c)
            except Exception:
                pass

    return all_containers


@router.get("/{container_id}", summary="Get Container")
async def get_container(container_id: str):
    """Get single container (async, non-blocking)"""
    try:
        c = await container_manager.get_container_async(container_id)
        return _serialize(c)
    except DockerUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")


@router.post("/", summary="Create Container (Disabled)")
@router.post("", summary="Create Container (Disabled)")
async def create_container(
    image: str = Query(..., description="Docker image (e.g. nginx:latest)"),
    name: str | None = Query(None, description="Container name"),
):
    """Disabled - use Jobs API for secure container orchestration"""
    raise HTTPException(status_code=403, detail="Direct container creation disabled. Use Jobs API instead.")


@router.delete("/{container_id}", summary="Stop/Delete Container")
async def delete_container(container_id: str):
    """Stop and remove a container (async, non-blocking)"""
    try:
        return await container_manager.stop_container_async(container_id, remove=True)
    except DockerUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError as e:
        raise HTTPException(status_code=400, detail=str(e))