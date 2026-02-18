"""Runqueue implementation for simpleCFS"""

from operator import attrgetter
from . import task

class Runqueue:
    def __init__(self):
        self.tasks = []

    def get_min_vruntime(self):
        """Returns minimum vruntime and the task associated."""
        return min(enumerate(self.tasks), key=lambda enum_pair: enum_pair[1].vruntime, default=None)
    
    def get_total_weight_from_queue(self):
        return sum(map(task.Task.get_task_weight, self.tasks))

    def add_task(self, task: task.Task):
        pass

    def pick_next_task(self):
        """Picks the next task to execute in the runqueue."""
        min = self.get_min_vruntime()

        if not min:
            return None
        return min[0]
