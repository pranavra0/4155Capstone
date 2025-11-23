# app/main.py
from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from api import nodes, containers, jobs, settings
from orchestrator import node_manager, container_manager

# Background task control
_background_task = None
_shutdown_event = None


async def sync_job_statuses():
    """Background task: sync job statuses and cleanup old containers"""
    from database import get_collection

    while not _shutdown_event.is_set():
        try:
            jobs_col = get_collection("jobs")
            nodes_dict = await node_manager.list_nodes_async()

            # Update running jobs based on container status
            running_jobs = list(jobs_col.find({"status": "running"}))

            async with httpx.AsyncClient(timeout=5.0) as client:
                for job in running_jobs:
                    node_id = job.get("node_id")
                    if not node_id:
                        continue

                    node_spec = nodes_dict.get(node_id)
                    if not node_spec or node_spec.get("status") != "online":
                        continue

                    try:
                        url = f"http://{node_spec['ip']}:{node_spec['port']}/containers?all=true"
                        resp = await client.get(url)
                        if resp.status_code == 200:
                            for c in resp.json():
                                if c.get("name") == f"job-{job['id']}":
                                    status = c.get("status", "").lower()
                                    if "exited" in status:
                                        new_status = "completed" if "(0)" in c.get("status", "") else "failed"
                                        jobs_col.update_one({"id": job["id"]}, {"$set": {"status": new_status}})
                                    break
                    except Exception:
                        pass

                # Auto-cleanup containers exited >1 hour
                for nid, spec in nodes_dict.items():
                    if spec.get("status") != "online":
                        continue
                    try:
                        url = f"http://{spec['ip']}:{spec['port']}/containers?all=true"
                        resp = await client.get(url)
                        if resp.status_code == 200:
                            for c in resp.json():
                                status = c.get("status", "").lower()
                                if "exited" in status and ("hour" in status or "day" in status):
                                    try:
                                        await client.delete(f"http://{spec['ip']}:{spec['port']}/containers/{c['id']}")
                                    except Exception:
                                        pass
                    except Exception:
                        pass

        except Exception:
            pass

        # Run every 30 seconds
        try:
            await asyncio.wait_for(_shutdown_event.wait(), timeout=30.0)
            break
        except asyncio.TimeoutError:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events"""
    global _background_task, _shutdown_event

    # Startup
    print("Starting orchestrator...")

    from database import init_db
    init_db()
    print("Database initialized")

    node_manager.start_monitoring()
    print("Node monitoring started")

    _shutdown_event = asyncio.Event()
    _background_task = asyncio.create_task(sync_job_statuses())
    print("Job status sync started")

    yield

    # Shutdown
    print("Shutting down orchestrator...")
    if _shutdown_event:
        _shutdown_event.set()
    if _background_task:
        try:
            await asyncio.wait_for(_background_task, timeout=5.0)
        except asyncio.TimeoutError:
            _background_task.cancel()

    await node_manager.shutdown()
    container_manager.shutdown()
    print("Cleanup complete")


app = FastAPI(
    title="Container Orchestrator",
    description="Distributed container orchestration system",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
app.include_router(containers.router, prefix="/containers", tags=["containers"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(settings.router, prefix="/settings", tags=["settings"])


@app.get("/")
def root():
    return {
        "message": "Container Orchestrator API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "nodes": len(node_manager.list_nodes()),
    }
