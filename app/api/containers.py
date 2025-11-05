# app/api/containers.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from docker.errors import APIError, NotFound

from orchestrator.container_manager import DockerUnavailable
from orchestrator import container_manager

router = APIRouter()


def _serialize(c) -> dict:
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

    return {"id": c.id, "name": name, "image": image, "status": status}


@router.get("/", summary="List Containers")
@router.get("", summary="List Containers")
async def list_containers(all: bool = Query(False, description="Include stopped/exited containers")):
    """List all containers (async, non-blocking)"""
    try:
        items = await container_manager.list_containers_async(all=all)
        return [_serialize(c) for c in items]
    except DockerUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))


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


@router.post("/", summary="Create Container")
@router.post("", summary="Create Container")
async def create_container(
    image: str = Query(..., description="Docker image (e.g. nginx:latest)"),
    name: str | None = Query(None, description="Container name"),
):
    """Create and start a container (async, non-blocking)"""
    try:
        return await container_manager.start_container_async(image=image, name=name)
    except DockerUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except APIError as e:
        raise HTTPException(status_code=400, detail=str(e))


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