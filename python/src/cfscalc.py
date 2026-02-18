"""Logic part for simpleCFS."""

from . import runqueue

class CFSCalculator:
    L = 6.0   #scheduler latency
    MIN_GRANULARITY = 0.75  #minimal granularity
    NICE_0_WEIGTH = 1024


    def calc_cur_time_slice(self, rqueue: runqueue.Runqueue) -> list:
        """Calculate the time slice for each task in the runqueue."""

        tot_weight = rqueue.get_total_weight_from_queue()
        slice = map(lambda t: self.L*t.get_task_weight()/tot_weight, rqueue.tasks)
        return list(slice)

    def update_vruntime(self, rqueue: runqueue.Runqueue) -> None:
        """Update the vruntime of each task in the runqueue."""

        for t in rqueue.tasks:
            t.vruntime = max(self.MIN_GRANULARITY, t.exec_time*self.NICE_0_WEIGTH/t.get_task_weight())

