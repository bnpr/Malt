# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import ctypes
import copy

from Malt.GL import *

from Malt.UBO import UBO
from Malt.Texture import TextureArray
from Malt.RenderTarget import ArrayLayerTarget, RenderTarget

from Malt.Render import Common

import glm

LIGHT_SUN = 1
LIGHT_POINT = 2
LIGHT_SPOT = 3

class C_Light(ctypes.Structure):
    _fields_ = [
        ('matrix', ctypes.c_float*16),
        ('color', ctypes.c_float*3),
        ('type', ctypes.c_int32),
        ('position', ctypes.c_float*3),
        ('radius', ctypes.c_float),
        ('direction', ctypes.c_float*3),
        ('spot_angle', ctypes.c_float),
        ('spot_blend', ctypes.c_float),
        ('type_index', ctypes.c_int32),
        ('__padding', ctypes.c_int32*2),
    ]

class C_LightsBuffer(ctypes.Structure):
    
    _fields_ = [
        ('lights', C_Light*128),
        ('lights_count', ctypes.c_int),
        ('__padding', ctypes.c_int32*3),
    ]


max_spots = 8
spot_resolution = 2048

max_suns = 8
sun_cascades = 8
sun_resolution = 2048

max_points = 8
point_resolution = 2048

class ShadowMaps(object):

    def __init__(self):
        self.spot_t = None
        self.spot_fbos = []

        self.sun_t = None
        self.sun_fbos = []

        self.initialized = False

    def setup(self):
        
        self.spot_t = TextureArray((spot_resolution, spot_resolution), max_spots, GL_DEPTH_COMPONENT32F)
        for i in range(self.spot_t.length):
            self.spot_fbos.append(RenderTarget(depth_stencil=ArrayLayerTarget(self.spot_t, i)))

        self.sun_t = TextureArray((sun_resolution, sun_resolution), max_suns * sun_cascades, GL_DEPTH_COMPONENT32F)
        for i in range(self.sun_t.length):
            self.sun_fbos.append(RenderTarget(depth_stencil=ArrayLayerTarget(self.sun_t, i)))

        #self.point = TextureArray(spot_resolution, max_points, GL_DEPTH_COMPONENT32F)

        self.initialized = True

    def load(self, scene):
        if self.initialized is False:
            self.setup()


class LightsBuffer(object):
    
    def __init__(self):
        self.data = C_LightsBuffer()
        self.UBO = UBO()
        self.shadowmaps = ShadowMaps()
        self.common_buffer = Common.CommonBuffer()
    
    def load(self, scene, pipeline, pass_name):
        scene = copy.copy(scene)
        scene.camera = copy.deepcopy(scene.camera)
        self.shadowmaps.load(scene)
        UBOS = {
            'COMMON_UNIFORMS' : self.common_buffer
        }
        spot_count = 0
        sun_count = 0
        point_count = 0

        for i, light in enumerate(scene.lights):
            self.data.lights[i].color = light.color
            self.data.lights[i].type = light.type
            self.data.lights[i].position = light.position
            self.data.lights[i].radius = light.radius
            self.data.lights[i].direction = light.direction
            self.data.lights[i].spot_angle = light.spot_angle
            self.data.lights[i].spot_blend = light.spot_blend

            if light.type == LIGHT_SPOT:
                self.data.lights[i].type_index = spot_count

                camera_matrix = glm.mat4(*light.matrix)
                #TODO: Hard-coded for Blender conventions for now
                projection_matrix = glm.perspectiveFovRH_NO(light.spot_angle, 1, 1, 0.01, light.radius)
                spot_matrix = projection_matrix * camera_matrix
                
                self.data.lights[i].matrix = tuple([e for vector in spot_matrix for e in vector])

                scene.camera.camera_matrix = light.matrix
                scene.camera.projection_matrix = tuple([e for vector in projection_matrix for e in vector])
                
                offset = pipeline.get_samples()[pipeline.sample_count]
                self.common_buffer.load(scene, (spot_resolution, spot_resolution), offset, pipeline.sample_count)

                self.shadowmaps.spot_fbos[spot_count].clear(depth=1)
                pipeline.draw_scene_pass(self.shadowmaps.spot_fbos[spot_count], 
                    scene.objects, pass_name, pipeline.default_shader[pass_name], UBOS)

                spot_count+=1
            
        self.data.lights_count = len(scene.lights)
        
        self.UBO.load_data(self.data)
    
    def bind(self, location):
        self.UBO.bind(location)

    def shader_callback(self, shader):
        shader.textures['SPOT_SHADOWMAPS'] = self.shadowmaps.spot_t

