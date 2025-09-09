from fastapi import FastAPI 
from api import containers, nodes, jobs
from database import init_db

app = FastAPI(title="Container Orchestrator")

app.include_router(containers.router, prefix="/containers", tags=["containers"])
app.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

@app.on_event("startup")
async def startup_event():
    init_db()
