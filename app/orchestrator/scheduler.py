import itertools
from orchestrator.models import Job, Node

class Scheduler:
    def __init__(self, strategy: str = "first_fit"):
        self.strategy = strategy
        self._rr_cycle = None

    def set_strategy(self, strategy: str):
        if strategy not in ["first_fit", "round_robin", "resource_aware"]:
            raise ValueError(f"Unknown scheduling strategy: {strategy}")
        self.strategy = strategy
        self._rr_cycle = None

    def get_strategy(self) -> str:
        return self.strategy

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
            return max(available_nodes, key=lambda node: (100 - (node.cpu_percent or 50)))

        else:
            raise ValueError(f"Unknown scheduling strategy: {self.strategy}")
    