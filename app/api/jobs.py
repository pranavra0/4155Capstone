from fastapi import APIRouter
from orchestrator.scheduler import Scheduler
from orchestrator.node_manager import NodeManager
from orchestrator.models import Job
from database import get_collection

router = APIRouter()
scheduler = Scheduler()
nm = NodeManager()

@router.post("/", response_model=dict)
async def submit_job(job: Job):
    jobs_collection = get_collection("jobs")
    available_nodes = list(nm.list_nodes().values())
    job_id, status_info = await scheduler.submit_job(job, available_nodes, delay=5)
    job.status = status_info["status"]
    job.node = status_info.get("node")
    jobs_collection.insert_one(job.dict())
    return {"job_id": job_id, "status": job.status, "node": job.node}

@router.get("/", response_model=list[Job])
def list_jobs():
    jobs_collection = get_collection("jobs")
    jobs = list(jobs_collection.find({}))
    return [Job(**j) for j in jobs]

@router.get("/status/{job_id}")
def get_job_status(job_id: str):
    return scheduler.get_status(job_id)
