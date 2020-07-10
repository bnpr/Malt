# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import ctypes

class CommonBuffer(ctypes.Structure):
    _fields_ = [
        ('CAMERA', ctypes.c_float*16),
        ('PROJECTION', ctypes.c_float*16),
        ('TIME', ctypes.c_float),
        ('FRAME', ctypes.c_int),
        ('SAMPLE', ctypes.c_int),
        ('__padding', ctypes.c_int),
    ]

