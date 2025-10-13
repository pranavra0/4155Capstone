# app/api/containers.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from docker.errors import APIError, NotFound

from orchestrator.container_manager import ContainerManager, DockerUnavailable

router = APIRouter()
cm = ContainerManager()


def _serialize(c) -> dict:
    """Convert a Docker SDK Container to a small, FE-friendly dict."""
    # name
    name = None
    try:
        name = getattr(c, "name", None)
        if not name:
            c.reload()
            # attrs["Name"] often has a leading "/"
            name = (c.attrs.get("Name", "") or "").lstrip("/")
    except Exception:
        name = None

    # image tag
    image = "<none>"
    try:
        tags = getattr(c.image, "tags", None)
        if tags:
            image = tags[0]
    except Exception:
        pass

    # status (running/exited/etc.)
    status = None
    try:
        status = getattr(c, "status", None)
    except Exception:
        pass

    return {"id": c.id, "name": name, "image": image, "status": status}


@router.get("/", summary="List Containers")
def list_containers(all: bool = Query(False, description="Include stopped/exited containers")):
    try:
        items = cm.list_containers(all=all)
        return [_serialize(c) for c in items]
    except DockerUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/{container_id}", summary="Get Container")
def get_container(container_id: str):
    try:
        c = cm.get_container(container_id)
        return _serialize(c)
    except DockerUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")


@router.post("/", summary="Create Container")
def create_container(
    image: str = Query(..., description="Docker image (e.g. nginx:latest)"),
    name: str | None = Query(None, description="Container name"),
):
    try:
        return cm.start_container(image=image, name=name)
    except DockerUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except APIError as e:
        # Common: 409 name in use, 404 pull denied, etc.
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{container_id}", summary="Stop/Delete Container")
def delete_container(container_id: str):
    try:
        return cm.stop_container(container_id, remove=True)
    except DockerUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError as e:
        raise HTTPException(status_code=400, detail=str(e))
