from fastapi import APIRouter
from orchestrator.scheduler import Scheduler
from orchestrator.node_manager import NodeManager
from orchestrator.models import Job

router = APIRouter()
scheduler = Scheduler()
nm = NodeManager()

@router.post("/", response_model=Job)
def submit_job(job: Job):
    node = scheduler.schedule_job(job, list(nm.list_nodes().keys()))
    job.status = "scheduled" if node else "failed"
    return job