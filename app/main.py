import os
import psutil
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import containers, nodes, jobs
from database import init_db
from orchestrator.node_manager import NodeManager
from datetime import datetime

# Heartbeat logger level via env (default INFO)
level = os.getenv("NODE_LOG_LEVEL", "INFO").upper()
logging.getLogger("orchestrator.node_heartbeat").setLevel(getattr(logging, level, logging.INFO))

app = FastAPI(title="Container Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(containers.router, prefix="/containers", tags=["containers"])
app.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

@app.on_event("startup")
async def startup_event():
    init_db()
    # create ONE shared NodeManager for the whole app
    app.state.nm = NodeManager()
    app.state.nm.start_monitoring()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/health")
def health():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
    }
