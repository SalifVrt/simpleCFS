

def format_task(line: list) -> list:
    """Format the task list to a [pid, arrival_time, nice, [calc_times], [I/O times]] format."""
    nline = [line[i] for i in range(2)]
    calcs = []
    io = []
    for i in range(2, len(line) - 1): #gather CPU tasks and I/O tasks together
        if i%2 == 0:
            calcs.append(line[i])
        else:
            io.append(line[i])

    nline = nline + [calcs] + [io]
    return nline