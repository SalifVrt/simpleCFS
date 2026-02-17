#import numpy as np
#import utils

MIN_GRANULARITY = 0.75  #granularité minimale
L = 6   #période d'ordonnancement
PRIO_TO_WEIGHT = [88761, 71755, 56483, 46273, 36291, 29154, 23254, 18705, 14949, 11916,
                  9548, 7620, 6100, 4904, 3906,
                  3121, 2501, 1991, 1586, 1277,
                  1024, 820, 655, 526, 423, 335, 272, 215, 172, 137,
                  110, 87, 70, 56, 45, 36, 29, 23, 18, 15]


def cfs_simp(tasks: list[int | list[int]], L: int=L, min_granularity: float=MIN_GRANULARITY) -> None :
    """
    Simplified CFS scheduler.
    
    tasks = list of formatted tasks (see format_task())
    L: int = Scheduling Period (in ms)
    min_granularity: int = Minimal Granluarity (in ms)
    """



    pass