import docker

class ContainerManager:
    def __init__(self):
        self.client = docker.from_env()
        
    def start_container(self, image: str, name: str):
        container = self.client.containers.run(image, name=name, detach=True)
        return container.id
    
    def stop_container(self, container_id: str):
        container = self.client.containers.get(container_id)
        container.stop()
        return True

    def list_containers(self, all: bool = False):
        return self.client.containers.list(all=all)

    def inspect(self, container_id: str):
        return self.client.containers.get(container_id)
