from fastapi import APIRouter
from orchestrator.scheduler import Scheduler
from orchestrator.node_manager import NodeManager
from orchestrator.models import Job
from database import get_collection

router = APIRouter()
scheduler = Scheduler()
nm = NodeManager()

@router.post("/", response_model=Job)
def submit_job(job: Job):
    jobs_collection = get_collection("jobs") 
    node = scheduler.schedule_job(job, list(nm.list_nodes().keys()))
    job.status = "scheduled" if node else "pending"
    jobs_collection.insert_one(job.dict())
    return job

@router.get("/", response_model=list[Job])
def list_jobs():
    jobs_collection = get_collection("jobs") 
    jobs = list(jobs_collection.find({}))
    return [Job(**j) for j in jobs]