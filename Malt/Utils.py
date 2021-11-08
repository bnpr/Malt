# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

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
        print(profiling_data.getvalue())

        return result
    
    return profiled_function

