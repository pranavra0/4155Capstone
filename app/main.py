from fastapi import FastAPI 
from api import containers, nodes, jobs
from fastapi.middleware.cors import CORSMiddleware
from database import init_db

app = FastAPI(title="Container Orchestrator")

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
    return {"message": "FastAPI Link: http://127.0.0.1:8000/docs#/"}
