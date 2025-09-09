
class NodeManager:
    def __init__(self):
        self.nodes = {}

    def register_node(self, node_id: str, resources: dict):
        """
        Register a new node with available resources.
        Example resources: {"cpu": 4, "memory": 8192}
        """
        self.nodes[node_id] = resources

    def list_nodes(self):
        """
        Return dict of all registered nodes.
        Example:
        {
          "node1": {"cpu": 4, "memory": 8192},
          "node2": {"cpu": 8, "memory": 16384}
        }
        """
        return self.nodes

    def get_node(self, node_id: str):
        """Get a single node by ID, or None if not found."""
        return self.nodes.get(node_id)

    def remove_node(self, node_id: str):
        """Remove a node from registry if it exists."""
        return self.nodes.pop(node_id, None)
