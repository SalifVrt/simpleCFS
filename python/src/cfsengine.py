"""simpleCFS Engine."""

from . import runqueue
from . import task
from . import logger
from . import cfscalc

class CFSEngine:
    def __init__(self, logger: logger.CFSLogger, tasks:list[task.Task]=[]):
        self.rqueue = runqueue.Runqueue()
        self.pending_tasks = sorted(tasks, key=lambda t: t.arrival_time)    #sort by arrival time
        self.waiting_for_io = []    #tasks in I/O with format (return_time, task)
        self.current_task = None
        self.time = 0.0
        self.logger = logger
        self.logic = cfscalc.CFSCalculator()
        #for time update in new scheduler events
        self.allocated_cpu_time = 0.0 
        self.cpu_stop_time = 0.0

    def run(self):
        self.logger.log_event(self.time, "START", message="CFS start")        

        while self.pending_tasks or (len(self.rqueue) > 0) or self.waiting_for_io or self.current_task:

            #next scheduler event
            next_event_candidates = []

            if self.pending_tasks:
                next_event_candidates.append((self.pending_tasks[0].arrival_time,"ARRIVAL"))

            if self.waiting_for_io:
                next_event_candidates.append((min(self.waiting_for_io)[0], "IO_RETURN"))

            if self.current_task is not None:
                next_event_candidates.append((self.cpu_stop_time, "CPU_STOP"))

            if not next_event_candidates:
                break #end of the simulation

            next_event = min(next_event_candidates)
    
            self.time = next_event[0]
            event_type = next_event[1]

            if event_type == "ARRIVAL":
                while self.pending_tasks and self.pending_tasks[0].arrival_time <= self.time:
                    new_task = self.pending_tasks.pop(0)
                    self.rqueue.add_task(new_task)
                    self.logger.log_event(self.time, "ARRIVAL", new_task)

            elif event_type == "IO_RETURN":
                self.waiting_for_io = sorted(self.waiting_for_io)
                while self.waiting_for_io and self.waiting_for_io[0][0] <= self.time:
                    new_task = self.waiting_for_io.pop(0)[1]
                    new_task.current_burst += 1
                    if new_task.current_burst >= len(new_task.bursts):
                        #task finished
                        new_task.end_time = self.time
                        self.logger.log_event(self.time, "TASK_END", new_task)

                    else:
                        #task having another burst
                        new_cur_burst = new_task.bursts[new_task.current_burst]

                        if new_cur_burst[0] == "CPU":
                            #return to runqueue
                            new_task.time_left_cur_burst = new_cur_burst[1]
                            self.rqueue.add_task(new_task)
                            self.logger.log_event(self.time, "RETURN_FROM_IO", new_task)

                        elif new_cur_burst[0] == "IO":
                            #go to I/O queue
                            return_time = self.time + new_cur_burst[1]
                            new_task.time_left_cur_burst = new_cur_burst[1]
                            self.waiting_for_io.append((return_time, new_task))
                            self.logger.log_event(self.time, "NEW_IO_BURST", new_task)
                

            elif event_type == "CPU_STOP":
                if self.current_task is not None:
                    self.current_task.exec_time += self.allocated_cpu_time
                    self.current_task.time_left_cur_burst -= self.allocated_cpu_time
                    self.logic.update_vruntime(self.current_task, self.allocated_cpu_time)

                    if self.current_task.time_left_cur_burst <= 0:
                        #if the burst is finished
                        self.current_task.current_burst += 1

                        if self.current_task.current_burst >= len(self.current_task.bursts):
                            #task finished
                            self.current_task.end_time = self.time
                            self.logger.log_event(self.time, "TASK_END", self.current_task)

                        else:
                            #task having another burst
                            new_cur_burst = self.current_task.bursts[self.current_task.current_burst]

                            if new_cur_burst[0] == "CPU":
                                #return to runqueue
                                self.current_task.time_left_cur_burst = new_cur_burst[1] 
                                self.rqueue.add_task(self.current_task)
                                self.logger.log_event(self.time, "NEW_CPU_BURST", self.current_task)

                            elif new_cur_burst[0] == "IO":
                                #go to I/O queue
                                return_time = self.time + new_cur_burst[1]
                                self.current_task.time_left_cur_burst = new_cur_burst[1]
                                self.waiting_for_io.append((return_time, self.current_task))
                                self.logger.log_event(self.time, "NEW_IO_BURST", self.current_task)

                                

                    else:
                        #time slice finished but not burst
                        self.rqueue.add_task(self.current_task)
                        self.logger.log_event(self.time, "TIME_SLICE_OVER", self.current_task)

                    self.current_task = None


            if self.current_task is None:
                # election of the new task on CPU
                next_task = self.rqueue.pick_next_task()
                
                if next_task:
                    self.current_task = next_task
                    
                    #for metrics
                    if self.current_task.start_time is None:
                        self.current_task.start_time = self.time
                    
                    cur_task_time_slice = self.logic.calc_cur_time_slice(self.rqueue, self.current_task)
                    self.allocated_cpu_time = min(cur_task_time_slice, self.current_task.time_left_cur_burst)
                    self.cpu_stop_time = self.time + self.allocated_cpu_time

                
            


            
            



