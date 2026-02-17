"""Runqueue implementation for simpleCFS"""

from operator import attrgetter
from task import Task

class Runqueue:
    def __init__(self):
        self.tasks = []

    def get_min_vruntime(self):
        return min(self.tasks, key=attrgetter('vruntime'), default=None)

    def add_task(self, task: Task):
        pass
