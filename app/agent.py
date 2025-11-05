# agent.py (run this on each worker node)
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
import psutil
import socket
from orchestrator.container_manager import ContainerManager, DockerUnavailable
from docker.errors import APIError, NotFound


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events"""
    yield
    # Cleanup on shutdown
    cm.shutdown()


app = FastAPI(title="Node Agent", lifespan=lifespan)
cm = ContainerManager()


@app.get("/health")
def health():
    """Health check endpoint - reports node status"""
    return {
        "hostname": socket.gethostname(),
        "status": "ok",
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory_percent": psutil.virtual_memory().percent
    }


@app.post("/containers")
async def create_container(
    image: str = Query(..., description="Docker image"),
    name: str = Query(None, description="Container name")
):
    """Create and start a container on this node"""
    try:
        result = await cm.start_container_async(image=image, name=name)
        return result
    except DockerUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except APIError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/containers")
async def list_containers():
    """List containers on this node"""
    try:
        containers = await cm.list_containers_async(all=False)
        return [
            {
                "id": c.id,
                "name": getattr(c, "name", None),
                "status": getattr(c, "status", None),
                "image": (getattr(c.image, "tags", None) or ["<none>"])[0] if hasattr(c, "image") else "<none>"
            }
            for c in containers
        ]
    except DockerUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.delete("/containers/{container_id}")
async def delete_container(container_id: str):
    """Stop and remove a container on this node"""
    try:
        result = await cm.stop_container_async(container_id, remove=True)
        return result
    except DockerUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)