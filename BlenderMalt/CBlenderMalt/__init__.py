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
    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
    ctypes.c_void_p, ctypes.c_int,
    ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), 
    ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint32)
]
retrieve_mesh_data.restype = None

retrieve_mesh_uv = CBlenderMalt['retrieve_mesh_uv']
retrieve_mesh_uv.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_float)]
retrieve_mesh_uv.restype = None

mesh_tangents_ptr = CBlenderMalt['mesh_tangents_ptr']
mesh_tangents_ptr.argtypes = [ctypes.c_void_p]
mesh_tangents_ptr.restype = ctypes.POINTER(ctypes.c_float)

pack_tangents = CBlenderMalt['pack_tangents']
pack_tangents.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.POINTER(ctypes.c_float)]
pack_tangents.restype = None

has_flat_polys = CBlenderMalt['has_flat_polys']
has_flat_polys.argtypes = [ctypes.c_void_p, ctypes.c_int]
has_flat_polys.restype = ctypes.c_bool

get_rect_ptr = CBlenderMalt['get_rect_ptr']
get_rect_ptr.argtypes = [ctypes.c_void_p]
get_rect_ptr.restype = ctypes.POINTER(ctypes.c_float)
