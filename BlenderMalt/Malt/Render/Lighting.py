# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import ctypes

LIGHT_SUN = 1
LIGHT_POINT = 2
LIGHT_SPOT = 3

class C_Light(ctypes.Structure):
    _fields_ = [
        ('color', ctypes.c_float*3),
        ('type', ctypes.c_int32),
        ('position', ctypes.c_float*3),
        ('radius', ctypes.c_float),
        ('direction', ctypes.c_float*3),
        ('spot_angle', ctypes.c_float),
        ('spot_blend', ctypes.c_float),
        ('__padding', ctypes.c_int32*3),
    ]

class LightsBuffer(ctypes.Structure):
    
    _fields_ = [
        ('lights', C_Light*128),
        ('lights_count', ctypes.c_int),
    ]

