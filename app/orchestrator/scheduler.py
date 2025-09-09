class Scheduler: 
    def __init__(self):
        #TODO impliment scheduling algos 
        pass
    
    def schedule_job(self, job, available_nodes):
        if not available_nodes:
            return None
        return available_nodes[0]
    
    