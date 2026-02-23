"""Logger implementation for simpleCFS."""

import typing
from . import task

class CFSLogger:
    def __init__(self, output_file=None):
        self.history = []
        self.output_file = output_file

    def log_event(self, time: float, event_type: str, task: typing.Optional[task.Task] = None, message: str = ""):
        """Save and show a system event."""
        timestamp = f"[{time:2f} ms]"

        if task:
            task_info = f"|Task {task.id:<3} (nice: {task.nice:>2}, vruntime {task.vruntime:>6.2f})"
        else:
            task_info = "| " + " " * 35 # Empty spacing to align columns

        log_line = f"{timestamp} {event_type:<10} {task_info} | {message}"
        self.history.append(log_line)

        self._write(log_line)

    def _write(self, message: str):
        """Manages the output (CLI or file)."""
        if self.output_file:
            with open(self.output_file, 'a') as f: #to add at the end of the file
                f.write(message + '\n')
        else:
            print(message)

    def print_summary(self, tasks):
        """Shows the simulation summary with metrics."""
        self._write("\n" + "="*85)
        self._write(f"{'SIMULATION FINISHED - STATS':^85}")
        self._write("="*85)

        header = f"| {'ID':<4} | {'Arrival':<7} | {'End':<9} | {'Turnaround':<9} | {'Waiting':<9} | {'CPU Tot':<7} | {'IO Tot':<7} |"
        self._write(header)
        self._write("-" * 85)

        total_turnaround = 0
        total_waiting = 0
        total_cpu_time = 0
        
        #avoid dividing by 0
        if not tasks:
            self._write("No task to show.")
            return

        for t in tasks:
            turnaround = t.end_time - t.arrival_time
            
            cpu_needed = sum(b[1] for b in t.bursts if b[0] == "CPU")
            io_needed = sum(b[1] for b in t.bursts if b[0] == "IO")
            
            #waiting
            waiting = turnaround - (cpu_needed + io_needed)
            
            if waiting < 0: waiting = 0.0

            total_turnaround += turnaround
            total_waiting += waiting
            total_cpu_time += cpu_needed

            line = f"| {t.id:<4} | {t.arrival_time:<7.2f} | {t.end_time:<9.2f} | {turnaround:<10.2f} | {waiting:<9.2f} | {cpu_needed:<7.2f} | {io_needed:<7.2f} |"
            self._write(line)

        self._write("-" * 85)

        #average
        n = len(tasks)
        avg_turnaround = total_turnaround / n
        avg_waiting = total_waiting / n
        
        #simulation end
        simulation_end_time = max(t.end_time for t in tasks) if tasks else 0
        cpu_utilization = (total_cpu_time / simulation_end_time * 100) if simulation_end_time > 0 else 0

        self._write(f"Average Turnaround : {avg_turnaround:.2f} ms")
        self._write(f"Average Waiting Time   : {avg_waiting:.2f} ms")
        self._write(f"Average CPU Use  : {cpu_utilization:.2f} %")
        self._write("="*85)