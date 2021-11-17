# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

import ctypes

from Malt.GL.Shader import UBO

class C_CommonBuffer(ctypes.Structure):
    _fields_ = [
        ('CAMERA', ctypes.c_float*16),
        ('PROJECTION', ctypes.c_float*16),
        ('RESOLUTION', ctypes.c_int*2),
        ('SAMPLE_OFFSET', ctypes.c_float*2),
        ('SAMPLE_COUNT', ctypes.c_int),
        ('FRAME', ctypes.c_int),
        ('TIME', ctypes.c_float),
        ('__padding', ctypes.c_int),
    ]

class CommonBuffer(object):
    
    def __init__(self):
        self.data = C_CommonBuffer()
        self.UBO = UBO()
    
    def load(self, scene, resolution, sample_offset=(0,0), sample_count=0, camera=None, projection = None):
        self.data.CAMERA = tuple(camera if camera else scene.camera.camera_matrix)
        self.data.PROJECTION = tuple(projection if projection else scene.camera.projection_matrix)
        self.data.RESOLUTION = resolution
        self.data.SAMPLE_OFFSET = sample_offset
        self.data.SAMPLE_COUNT = sample_count
        self.data.FRAME = scene.frame
        self.data.TIME = scene.time

        self.UBO.load_data(self.data)
    
    def bind(self, location):
        self.UBO.bind(location)


