"""simpleCFS Engine."""

from . import runqueue
from . import task

class CFSEngine:
    def __init__(self, tasks:list[task.Task]=[]):
        self.rqueue = runqueue.Runqueue()
        self.tasks = tasks
        self.time = 0.0

    def run(self):
        pass


def main():
    pass