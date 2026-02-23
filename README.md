# simpleCFS

> A simplified implementation of the **Completely Fair Scheduler (CFS)** from the Linux kernel.

---

## Overview

`simpleCFS` simulates the core scheduling logic of Linux's CFS on a **single-core processor**. It is intentionally stripped down for clarity and pedagogical purposes, replacing complex data structures (red-black trees, interactive heuristics) with a straightforward linear runqueue.

The scheduler aims to give every task a fair share of CPU time, weighted by priority, using the concept of **virtual runtime** (`vruntime`).

---

## simpleCFS vs. Linux CFS

| Feature | Linux CFS | simpleCFS |
|---|---|---|
| Data structure | Red-black tree | Linear runqueue scan |
| Multi-core / SMP | ✅ | ❌ (single core only) |
| Task migration | ✅ | ❌ |
| Interactive latency | ✅ | ❌ |
| Wakeup preemption | ✅ | ❌ |
| Time unit | nanoseconds | milliseconds (2 decimal places) |

---

## Scheduling Parameters

| Parameter | Symbol | Default value |
|---|---|---|
| Minimum granularity | Δ | `0.75 ms` |
| Scheduling period | L | `6.00 ms` |

---

## How It Works

### Virtual Runtime (`vruntime`)

Each task accumulates `vruntime` proportionally to the real time it runs, weighted by its priority. The scheduler always picks the task with the **lowest `vruntime`** — the one that has received the least fair share of CPU time.

> **Note:** `vruntime` is updated **only at scheduler invocation**, not continuously.

### Scheduler Triggers

The scheduler is invoked when:
- The current task's **time slice expires**
- The current task **finishes** execution
- The current task **enters I/O wait**

### Fairness at Insertion

When a new task enters the runqueue (fresh start or return from I/O), its initial `vruntime` is set to the **minimum `vruntime`** among all tasks currently in the runqueue. This prevents starvation of existing tasks.

### No Immediate Preemption on I/O Return

When a task returns from I/O, it is inserted into the runqueue **without immediately preempting** the currently running task — even if its `vruntime` lag is significant.

---

## Project Structure

```
simpleCFS/
├── src/
│   ├── cfsengine.py # Core CFS scheduling logic
│   ├── cfscalc.py # CFS logic helper class (calculations)
│   ├── utils.py # Helper functions for formatting input file
│   ├── main.py # Entry program for simpleCFS
│   ├── logger.py # Logger class for simulation logs
│   ├── task.py      # Task model (vruntime, priority, state)
│   └── runqueue.py  # Linear runqueue implementation
├── tests/
│   └── ...          # Unit tests
├── pyproject.toml
├── LICENSE
├── Makefile
└── README.md
```

---

## Getting Started

### Prerequisites

- [Python 3.14+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) — fast Python package manager

### Install

```bash
make install   # uv pip install -e .
make sync      # uv sync (lock file)
```

### Run

```bash
make run FILE=<your_input_file>
```

The `FILE` argument is passed directly to the `scfs` command (switch to default file if no file is specified):

```bash
# Example
make run FILE=scenarios/example.txt
```

---

## Development

### Run tests

```bash
make test
```

### Cleanup

```bash
make clean   # removes .pytest_cache and __pycache__ directories
```

---

## References

- [CFS Scheduler — Linux kernel documentation](https://www.kernel.org/doc/html/latest/scheduler/sched-design-CFS.html)
- [Completely Fair Scheduler — Wikipedia](https://en.wikipedia.org/wiki/Completely_Fair_Scheduler)

[Repository link](https://github.com/SalifVrt/simpleCFS)