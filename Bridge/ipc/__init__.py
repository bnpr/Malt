import subprocess
import os
import ctypes

import platform

src_dir = os.path.abspath(os.path.dirname(__file__))

library = 'libIpc.so'
if platform.system() == 'Windows': library = 'Ipc.dll'
if platform.system() == 'Darwin': library = 'libIpc.dylib'

Ipc = ctypes.CDLL(os.path.join(src_dir, library))

class C_SharedMemory(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('data', ctypes.c_void_p),
        ('size', ctypes.c_size_t),
        ('handle', ctypes.c_void_p),
        ('int', ctypes.c_int),
    ]

create_shared_memory = Ipc['create_shared_memory']
create_shared_memory.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
create_shared_memory.restype = C_SharedMemory

open_shared_memory = Ipc['open_shared_memory']
open_shared_memory.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
open_shared_memory.restype = C_SharedMemory

close_shared_memory = Ipc['close_shared_memory']
close_shared_memory.argtypes = [C_SharedMemory]
close_shared_memory.restype = None

__BUFFERS = {}
class SharedMemory(object):
    def __init__(self, name, size, gen):
        self.name = ('MALT_SHARED_MEM_' + name + '_GEN_' + str(gen)).encode('ascii')
        self.size = size
        self.gen = gen
        self.c = create_shared_memory(self.name, self.size)
    
    def __del__(self):
        close_shared_memory(self.c)

class SharedMemoryRef(object):
    def __init__(self, full_name, size):
        self.name = full_name
        self.size = size
        self.c = open_shared_memory(self.name, self.size)
    
    def __del__(self):
        close_shared_memory(self.c)

def load_shared_buffer(name, ctype, size):
    total_size = ctypes.sizeof(ctype) * size
    if name not in __BUFFERS:
        __BUFFERS[name] = SharedMemory(name, total_size, 0)
    elif total_size > __BUFFERS[name].size:
        old = __BUFFERS[name]
        __BUFFERS[name] = SharedMemory(name, total_size, old.gen + 1)
        del old
    
    return (ctype * size).from_address(__BUFFERS[name].c.data)

def get_shared_buffer_full_name(name):
    return __BUFFERS[name].name


