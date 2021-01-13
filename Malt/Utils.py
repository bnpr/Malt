# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

LOG_MODES = [
    'NONE',
    'USER',
    'WARNING',
    'DEBUG',
    'FULL'
]

LOG_MODE = 'USER'

def log(mode, *messages):
    if LOG_MODES.index(mode) <= LOG_MODES.index(LOG_MODE):
        for message in messages:
            print(message)


import cProfile, io, pstats

class ScopedProfile(object):

    def __init__(self, profiling_data=io.StringIO()):
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        self.profiling_data = profiling_data

    def __del__(self):
        self.profiler.disable()
        stats = pstats.Stats(self.profiler, stream=self.profiling_data)
        stats.strip_dirs()
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats()

