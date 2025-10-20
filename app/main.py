import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import containers, nodes, jobs
from database import init_db
from orchestrator.node_manager import NodeManager
from datetime import datetime


app = FastAPI(title="Container Orchestrator")
nm = NodeManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(containers.router, prefix="/containers", tags=["containers"])
app.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

@app.on_event("startup")
async def startup_event():
    init_db()
    nm.start_monitoring()

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