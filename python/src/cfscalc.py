"""Logic part for simpleCFS."""

from . import runqueue
from . import task

class CFSCalculator:
    L = 6.0   # scheduler latency (target period)
    MIN_GRANULARITY = 0.75  # minimal granularity
    NICE_0_WEIGHT = 1024

    def calc_cur_time_slice(self, rqueue: runqueue.Runqueue, task: task.Task) -> float:
        """Calculate the time slice for a task."""

        queue_weight = rqueue.get_total_weight_from_queue()
        current_weight = task.get_task_weight()
        
        # If task is already in the queue, don't add its weight again
        if task in rqueue.tasks:
            total_active_weight = queue_weight
        else:
            total_active_weight = queue_weight + current_weight

        if total_active_weight == 0: #to avoid dividing by 0
            return self.L

        slice_val = self.L * (current_weight / total_active_weight)
        return max(slice_val, self.MIN_GRANULARITY)

    def update_vruntime(self, current_task: task.Task, actual_duration: float) -> None:
        """Update the vruntime based on actual execution time."""
        
        weight_factor = self.NICE_0_WEIGHT / current_task.get_task_weight()
        current_task.vruntime += actual_duration * weight_factor
