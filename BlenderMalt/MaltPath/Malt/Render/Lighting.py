# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import ctypes
from Malt.UBO import UBO

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

class C_LightsBuffer(ctypes.Structure):
    
    _fields_ = [
        ('lights', C_Light*128),
        ('lights_count', ctypes.c_int),
        ('__padding', ctypes.c_int32*3),
    ]

class LightsBuffer(object):
    
    def __init__(self):
        self.data = C_LightsBuffer()
        self.UBO = UBO()
    
    def load(self, scene):
        for i, light in enumerate(scene.lights):
            self.data.lights[i].color = light.color
            self.data.lights[i].type = light.type
            self.data.lights[i].position = light.position
            self.data.lights[i].radius = light.radius
            self.data.lights[i].direction = light.direction
            self.data.lights[i].spot_angle = light.spot_angle
            self.data.lights[i].spot_blend = light.spot_blend
        self.data.lights_count = len(scene.lights)
        
        self.UBO.load_data(self.data)
    
    def bind(self, location):
        self.UBO.bind(location)
