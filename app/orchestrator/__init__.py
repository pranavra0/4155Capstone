# app/orchestrator/__init__.py
from .node_manager import NodeManager
from .container_manager import ContainerManager
from .scheduler import Scheduler

# Create singleton instances to share across all API routes
node_manager = NodeManager()
container_manager = ContainerManager()
scheduler = Scheduler()