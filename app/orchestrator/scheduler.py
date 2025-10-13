import itertools
import asyncio
import uuid
from orchestrator.models import Job, Node

class Scheduler:
    def __init__(self, strategy: str = "first_fit"):
        self.strategy = strategy
        self._rr_cycle = None
        self.tasks = {}  # Track running async tasks
    
    def schedule_job(self, job, available_nodes: list[Node]) -> Node | None:
        if not available_nodes:
            return None
        
        if self.strategy == "first_fit":
            return available_nodes[0]
        
        elif self.strategy == "round_robin":
            if self._rr_cycle is None:
                self._rr_cycle = itertools.cycle(available_nodes)
            return next(self._rr_cycle)
        
        elif self.strategy == "resource_aware":
            return max(available_nodes, key=lambda node: node.cpu)
        
        else:
            raise ValueError(f"Unknown scheduling strategy: {self.strategy}")
    
    async def _run_async_job(self, job_id: str, job: Job, delay: int):
        print(f"Task {job_id} started with a delay of {delay} seconds")
        await asyncio.sleep(delay)
        print(f"Task {job_id} finished")
        return f"Job {job_id} completed after {delay} seconds"
    
    async def submit_job(self, job: Job, available_nodes: list[Node], delay: int = 3):
        node = self.schedule_job(job, available_nodes)
        if not node:
            return None, {"status": "no available nodes"}
        
        job_id = str(uuid.uuid4())
        task = asyncio.create_task(self._run_async_job(job_id, job, delay))
        self.tasks[job_id] = task
        
        return job_id, {"status": "scheduled", "node": node.name}
    
    def get_status(self, job_id: str):
        task = self.tasks.get(job_id)
        if not task:
            return {"status": "not found"}
        if task.done():
            try:
                return {"status": "completed", "result": task.result()}
            except Exception as e:
                return {"status": "failed", "error": str(e)}
        return {"status": "running"}
