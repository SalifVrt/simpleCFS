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
        """Shows the simulation summary."""
        self._write("\n" + "="*50)
        self._write("SIMULATION TERMINEE - STATISTIQUES")
        self._write("="*50)