import logging

class MaltLogger():

    def __init__(self):
        self.last_msg = None
        self.repeated_msg = 0
    
    def log(self, level, *args):
        if level < logging.root.level:
            return
        args = [str(arg) for arg in args]
        msg = ' '.join(args)
        if msg != self.last_msg:
            self.last_msg = msg
            self.repeated_msg = 0
            logging.log(level, msg)
        else:
            self.repeated_msg += 1
            if self.repeated_msg in (1, 10, 100, 1000):
                logging.log(level, '(Repeated {}+ times)'.format(self.repeated_msg))

    def debug(self, *args):
        self.log(logging.DEBUG, *args)

    def info(self, *args):
        self.log(logging.INFO, *args)

    def warning(self, *args):
        self.log(logging.WARNING, *args)

    def error(self, *args):
        self.log(logging.ERROR, *args)

    def critical(self, *args):
        self.log(logging.CRITICAL, *args)

LOG = MaltLogger()
        

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

def isinstance_str(object, class_name):
    classes = [object.__class__, *object.__class__.__bases__]
    for cls in classes:
        if cls.__name__ == class_name:
            return True
    return False

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

# https://numpy.org/doc/stable/reference/arrays.interface.html
class Array_Interface():
    def __init__(self, pointer, typestr, shape, read_only=False):
        self.__array_interface__ = {
            'data': (pointer, read_only),
            'typestr': typestr,
            'shape': shape
        }

class IBuffer():

    def ctype(self):
        raise Exception('ctype() method not implemented')
    
    def __len__(self):
        raise Exception('__len__() method not implemented')
    
    def buffer(self):
        raise Exception('buffer() method not implemented')
    
    def size_in_bytes(self):
        import ctypes
        return ctypes.sizeof(self.ctype()) * len(self)
    
    def as_array_interface(self, shape=None):
        import ctypes
        type_map = {
            ctypes.c_float : 'f',
            ctypes.c_int : 'i',
            ctypes.c_uint : 'u',
            ctypes.c_bool : 'b',
        }
        
        if shape is None:
            shape = (len(self),)

        return Array_Interface(
            ctypes.addressof(self.buffer()),
            type_map[self.ctype()],
            shape
        )
    
    def as_np_array(self, shape=None):
        import numpy as np
        return np.array(self.as_array_interface(shape), copy=False)
