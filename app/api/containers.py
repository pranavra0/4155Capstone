from fastapi import APIRouter
from orchestrator.container_manager import ContainerManager
from orchestrator.models import Container 

router = APIRouter()
cm = ContainerManager() 

@router.post("/", response_model=Container)
def create_container(image: str, name: str):
    container_id = cm.start_container(image, name)
    return Container(id=container_id, image=image, status="running")

@router.get("/", response_model=list[Container])
def list_containers():
    containers = cm.list_containers()
    return [Container(id=c.id, image=c.image.tags[0] if c.image.tags else "unknown", status=c.status) for c in containers]
    
@router.delete("/{container_id}")
def stop_container(container_id: str):
    cm.stop_container(container_id)
    return {"status": "stopped", "id": container_id}
