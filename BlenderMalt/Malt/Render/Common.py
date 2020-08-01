# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import ctypes
from ..UBO import UBO

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
    
    def load(self, scene, resolution, sample_offset, sample_count):
        #Setup camera jitter
        offset_x = sample_offset[0] / resolution[0]
        offset_y = sample_offset[1] / resolution[1]

        if scene.camera.projection_matrix[-1] == 1.0:
            #Orthographic camera
            scene.camera.projection_matrix[12] += offset_x
            scene.camera.projection_matrix[13] += offset_y
        else:
            #Perspective camera
            scene.camera.projection_matrix[8] += offset_x
            scene.camera.projection_matrix[9] += offset_y

        self.data.CAMERA = tuple(scene.camera.camera_matrix)
        self.data.PROJECTION = tuple(scene.camera.projection_matrix)
        self.data.RESOLUTION = resolution
        self.data.SAMPLE_OFFSET = sample_offset
        self.data.SAMPLE_COUNT = sample_count
        self.data.FRAME = scene.frame
        self.data.TIME = scene.time

        self.UBO.load_data(self.data)
    
    def bind(self, location):
        self.UBO.bind(location)


