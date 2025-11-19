# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import nodes, containers, jobs, settings
from orchestrator import node_manager, container_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events"""
    # Startup
    print("🚀 Starting orchestrator...")

    # Initialize database
    from database import init_db
    init_db()
    print("✅ Database initialized")

    node_manager.start_monitoring()
    print("✅ Node monitoring started")

    yield

    # Shutdown
    print("🛑 Shutting down orchestrator...")
    await node_manager.shutdown()
    container_manager.shutdown()
    print("✅ Cleanup complete")


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
