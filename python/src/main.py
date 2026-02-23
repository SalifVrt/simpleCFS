"""Main script for simpleCFS."""

import argparse
from . import cfsengine
from . import logger
from . import utils
from . import task

def main():
    parser = argparse.ArgumentParser(description="Simulateur simpleCFS")
    parser.add_argument(
            "filepath", 
            nargs="?", 
            default="tests/testfiles/td1.txt", 
            help="Chemin vers le fichier de tâches (défaut: td1.txt)"
        )    
    args = parser.parse_args()

    print(f"Démarrage de simpleCFS avec le fichier : {args.filepath} ...\n")

    raw_tasks_data = utils.file_to_tasks(args.filepath)

    tasks = []
    for data in raw_tasks_data:
        # data is like : ['A', 0, 0, [('CPU', 1), ('IO', 8)]]
        new_task = task.Task(
            task_id=data[0],
            arrival_time=float(data[1]),
            task_nice=int(data[2]),
            bursts=data[3]
        )
        tasks.append(new_task)

    #simulation start
    sim_logger = logger.CFSLogger()
    engine = cfsengine.CFSEngine(logger=sim_logger, tasks=tasks)
    
    engine.run()

    #summary
    sim_logger.print_summary(tasks)

if __name__ == "__main__":
    main()