import subprocess
import os
import ctypes

import platform

src_dir = os.path.abspath(os.path.dirname(__file__))

library = 'libCBlenderMalt.so'
if platform.system() == 'Windows': library = 'CBlenderMalt.dll'
if platform.system() == 'Darwin': library = 'libCBlenderMalt.dylib'

CBlenderMalt = ctypes.CDLL(os.path.join(src_dir, library))

retrieve_mesh_data = CBlenderMalt['retrieve_mesh_data']
retrieve_mesh_data.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_int), ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint32)
]
retrieve_mesh_data.restype = None

mesh_tangents_ptr = CBlenderMalt['mesh_tangents_ptr']
mesh_tangents_ptr.argtypes = [ctypes.c_void_p]
mesh_tangents_ptr.restype = ctypes.POINTER(ctypes.c_float)
