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

def profile_function(function):
    def profiled_function(*args, **kwargs):
        profiler = cProfile.Profile()
        profiling_data = io.StringIO()
        profiler.enable()

        function(*args, **kwargs)

        profiler.disable()
        stats = pstats.Stats(profiler, stream=profiling_data)
        stats.strip_dirs()
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats()
        print(profiling_data.getvalue())
    
    return profiled_function

