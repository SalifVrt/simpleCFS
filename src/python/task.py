"""Task representation for simpleCFS"""

class Task:
    def __init__(self, task_id: str, arrival_time: float, task_nice: int, bursts: list[tuple[float, int]]):
        self.id: str = task_id
        self.nice: int = task_nice
        self.vruntime: float = 0.0
        self.state: (None | str) = None
        self.arrival_time = arrival_time
        self.bursts = bursts #burst ex: ("CPU", 9)
        self.current_burst: int = 0

    def is_finished(self):
        return self.current_burst == len(self.bursts)

    