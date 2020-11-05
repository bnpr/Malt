import subprocess
import os
import ctypes

src_dir = os.path.abspath(os.path.dirname(__file__))

CMalt = ctypes.CDLL(os.path.join(src_dir, 'CMalt'))

retrieve_mesh_data = CMalt['retrieve_mesh_data']
retrieve_mesh_data.argtypes = [
    ctypes.c_void_p, 
    ctypes.c_void_p, ctypes.c_int, 
    ctypes.c_void_p, ctypes.c_int,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_int16), 
    ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint32)
]
retrieve_mesh_data.restype = None

retrieve_mesh_uv = CMalt['retrieve_mesh_uv']
retrieve_mesh_uv.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_float)]
retrieve_mesh_uv.restype = None

has_flat_polys = CMalt['has_flat_polys']
has_flat_polys.argtypes = [ctypes.c_void_p, ctypes.c_int]
has_flat_polys.restype = ctypes.c_bool
