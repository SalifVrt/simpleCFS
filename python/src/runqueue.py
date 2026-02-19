"""Runqueue implementation for simpleCFS"""

from . import task

class Runqueue:
    def __init__(self):
        self.tasks = []

    def get_min_vruntime(self):
        """Return minimum vruntime and the task associated."""
        return min(enumerate(self.tasks), key=lambda enum_pair: enum_pair[1].vruntime, default=None)
    
    def get_total_weight_from_queue(self):
        """Return sum of the weights of all the tasks in the runqueue."""
        return sum(map(task.Task.get_task_weight, self.tasks))

    def add_task(self, task: task.Task):
        """Add a new task to runqueue."""

        min_vruntime = self.get_min_vruntime()
        if min_vruntime:
            task.vruntime = max(min_vruntime[1], task.vruntime)
        self.tasks.append(task)


    def pick_next_task(self):
        """Pick the next task to execute in the runqueue."""

        min = self.get_min_vruntime()
        if not min:
            return None
        return min[0]
