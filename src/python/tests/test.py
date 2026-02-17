import utils
import runqueue
import task

#Test format
ts = utils.file_to_tasks("tests/testfiles/td1.txt")
print(ts)

#Test task
t = task.Task(ts[1][0], ts[1][1], ts[1][2], ts[1][3])
print(f"Task {t.id}: arrival {t.arrival_time}, nice {t.nice}, bursts {t.bursts}")