from fastapi import APIRouter, Query
from orchestrator.container_manager import ContainerManager
from orchestrator.models import Container

router = APIRouter()
cm = ContainerManager()

@router.post("/", response_model=Container)
def create_container(image: str, name: str):
    container_id = cm.start_container(image, name)
    return Container(id=container_id, image=image, status="running")

@router.get("/", response_model=list[Container])
def list_containers(all: bool = Query(False, description="Include stopped containers")):
    items = cm.list_containers(all=all)
    result = []
    for c in items:
        image = c.image.tags[0] if getattr(c.image, "tags", None) else c.image.short_id
        status = getattr(c, "status", "unknown")
        result.append(Container(id=c.id, image=str(image), status=status))
    return result

@router.get("/{container_id}", response_model=Container)
def get_container(container_id: str):
    c = cm.inspect(container_id)
    image = c.image.tags[0] if getattr(c.image, "tags", None) else c.image.short_id
    status = getattr(c, "status", "unknown")
    return Container(id=c.id, image=str(image), status=status)

@router.delete("/{container_id}")
def stop_container(container_id: str):
    cm.stop_container(container_id)
    return {"status": "stopped", "id": container_id}
