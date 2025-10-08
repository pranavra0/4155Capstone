from fastapi import FastAPI 
from api import containers, nodes, jobs
from fastapi.middleware.cors import CORSMiddleware
from database import init_db

from orchestrator.container_manager import ContainerManager
from orchestrator.node_manager import NodeManager
from database import get_collection

app = FastAPI(title="Container Orchestrator")

cm = ContainerManager()
nm = NodeManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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

@app.get("/")
def root():
    return {
        "message": "FastAPI API is working",
        "docs": "http://127.0.0.1:8000/docs",
        "routes": {
            "containers": "/containers",
            "nodes": "/nodes",
            "jobs": "/jobs"
        }
    }

@app.get("/status")
def status():
    jobs_collection = get_collection("jobs")
    return {
        "nodes_registered": len(nm.list_nodes()),
        "jobs_total": jobs_collection.count_documents({}),
        "containers_running": len(cm.client.containers.list())
    }

