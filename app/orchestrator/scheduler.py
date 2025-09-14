import itertools
from orchestrator.models import Job, Node

class Scheduler: 
    def __init__(self, strategy: str = "first_fit"):
        self.strategy = strategy
        self._rr_cycle = None
    
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
            # subject to change
            return max(available_nodes, key=lambda node: node.cpu)

        else:
            raise ValueError(f"Unknown scheduling strategy: {self.strategy}")
    