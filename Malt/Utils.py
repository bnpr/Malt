# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

import logging as LOG

def dump_function(function):
    import textwrap, inspect
    name = function.__name__
    function = textwrap.dedent(inspect.getsource(function))
    return (name, function)

def load_function(function):
    name, function = function
    f = {}
    exec(function, f)
    return f[name]

def scan_dirs(path, file_callback):
    import os
    for e in os.scandir(path):
        if e.is_file():
            file_callback(e)
        if e.is_dir():
            scan_dirs(e, file_callback)

import cProfile, io, pstats

def profile_function(function):
    def profiled_function(*args, **kwargs):
        profiler = cProfile.Profile()
        profiling_data = io.StringIO()
        profiler.enable()

        result = function(*args, **kwargs)

        profiler.disable()
        stats = pstats.Stats(profiler, stream=profiling_data)
        stats.strip_dirs()
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats()
        print('PROFILE FUNCTION: ', function.__name__)
        print(profiling_data.getvalue())

        return result
    
    return profiled_function

