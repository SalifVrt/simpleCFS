"""Task representation for simpleCFS"""

PRIO_TO_WEIGHT = [88761, 71755, 56483, 46273, 36291, 29154, 23254, 18705, 14949, 11916,
                  9548, 7620, 6100, 4904, 3906,
                  3121, 2501, 1991, 1586, 1277,
                  1024, 820, 655, 526, 423, 335, 272, 215, 172, 137,
                  110, 87, 70, 56, 45, 36, 29, 23, 18, 15]

class Task:
    def __init__(self, task_id: str, arrival_time: float, task_nice: int, bursts: list[tuple]):
        self.id: str = task_id
        self.nice: int = task_nice
        self.vruntime: float = 0.0
        self.state: (None | str) = None
        self.arrival_time = arrival_time
        self.bursts = bursts    #burst ex: ("CPU", 9)
        self.current_burst: int = 0
        self.exec_time = 0.0    #cumulative time on CPU

    def is_finished(self):
        return self.current_burst == len(self.bursts)
    
    def get_task_weight(self):
        return PRIO_TO_WEIGHT[self.nice+20]

    