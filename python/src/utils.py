"""Utils for formatting input file containing tasks"""

def format_task(line: list) -> list:
    """Format the task list to a [pid, arrival_time, [(task_type, time), ...]] format."""
    nline = [line[i] for i in range(3)]
    tasks = []
    for i in range(3, len(line)):  # gather CPU and I/O tasks as tuples
        if (i - 3) % 2 == 0:
            tasks.append(("CPU", line[i]))
        else:
            tasks.append(("IO", line[i]))

    nline = nline + [tasks]
    return nline

def file_to_tasks(filename: str) -> list:
    """"""
    f = open(filename, "r")
    lines = f.readlines()

    f_lines = []
    for line in lines:
        s_line = line.strip("\n").split()
        str_to_int_line = [s_line[0]] + [int(s_line[i]) for i in range(1, len(s_line))]
        f_lines.append(format_task(str_to_int_line))

    return f_lines
