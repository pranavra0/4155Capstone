# app/api/jobs.py
from fastapi import APIRouter, HTTPException
import httpx
import asyncio
from orchestrator.models import Job, Node
from database import get_collection
from orchestrator import scheduler, node_manager

router = APIRouter()


@router.post("/", response_model=Job)
@router.post("", response_model=Job)
async def submit_job(job: Job):
    """Submit a job and deploy to available node"""
    jobs_collection = get_collection("jobs")

    # Get available nodes asynchronously
    nodes_dict = await node_manager.list_nodes_async()
    available_nodes = [
        Node(
            id=nid,
            ip=spec["ip"],
            port=spec["port"],
            cpu=spec["cpu"],
            memory=spec["memory"],
            status=spec.get("status", "unknown"),
            cpu_percent=spec.get("cpu_percent"),
            memory_percent=spec.get("memory_percent")
        )
        for nid, spec in nodes_dict.items()
        if spec.get("status") == "online"
    ]

    if not available_nodes:
        job.status = "pending"
        # Store in DB using thread executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: jobs_collection.insert_one(job.dict()))
        return job

    # Schedule job to a node
    target_node = scheduler.schedule_job(job, available_nodes)

    if target_node:
        # Deploy container to remote node
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"http://{target_node.ip}:{target_node.port}/containers"
                resp = await client.post(url, params={"image": job.image, "name": f"job-{job.id}"})

                if resp.status_code == 200:
                    job.status = "running"
                    container_info = resp.json()
                    # You could store container_info in job if needed
                else:
                    job.status = "failed"
        except Exception as e:
            print(f"Failed to deploy job {job.id}: {e}")
            job.status = "failed"
    else:
        job.status = "pending"

    # Store job in database
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: jobs_collection.insert_one(job.dict()))

    return job


@router.get("/", response_model=list[Job])
@router.get("", response_model=list[Job])
async def list_jobs():
    """List all jobs"""
    jobs_collection = get_collection("jobs")
    
    # Run MongoDB query in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    jobs = await loop.run_in_executor(None, lambda: list(jobs_collection.find({})))
    
    return [Job(**j) for j in jobs]


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get single job"""
    jobs_collection = get_collection("jobs")
    
    loop = asyncio.get_event_loop()
    job = await loop.run_in_executor(None, lambda: jobs_collection.find_one({"id": job_id}))
    
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return Job(**job)


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Delete a job"""
    jobs_collection = get_collection("jobs")
    
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, lambda: jobs_collection.delete_one({"id": job_id}))
    
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"status": "deleted", "id": job_id}