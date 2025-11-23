# agent.py (run this on each worker node)
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# Enable CORS for auto-detect feature from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cm = ContainerManager()


@app.get("/health")
def health():
    """Health check endpoint - reports node status"""
    mem = psutil.virtual_memory()
    return {
        "hostname": socket.gethostname(),
        "status": "ok",
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory_percent": mem.percent,
        "cpu_count": psutil.cpu_count(),
        "memory_total_mb": round(mem.total / (1024 * 1024))
    }


@app.post("/containers")
async def create_container(
    image: str = Query(..., description="Docker image"),
    name: str = Query(None, description="Container name"),
    command: str = Query(None, description="Command to run in container")
):
    """Create and start a container on this node"""
    try:
        result = await cm.start_container_async(image=image, name=name, command=command)
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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001, help="Port to run agent on")
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)