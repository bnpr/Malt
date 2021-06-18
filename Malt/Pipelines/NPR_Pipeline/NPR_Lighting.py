# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import logging as log
from Malt.GL.GL import *
from Malt.GL.Shader import UBO
from Malt.GL.Texture import TextureArray, CubeMapArray
from Malt.GL.RenderTarget import ArrayLayerTarget, RenderTarget

from Malt.Render import Common
from Malt.Render import Lighting
from Malt.Render.Lighting import LightsBuffer, ShadowMaps

from Malt import Pipeline

_SHADOWMAPS = None

def get_shadow_maps():
    if Pipeline.MAIN_CONTEXT:
        global _SHADOWMAPS
        if _SHADOWMAPS is None: _SHADOWMAPS = (NPR_ShadowMaps(), NPR_TransparentShadowMaps())
        return _SHADOWMAPS
    else:
        return (NPR_ShadowMaps(), NPR_TransparentShadowMaps())


class C_NPR_LightGroupsBuffer(ctypes.Structure):
    _fields_ = [
        ('light_group_index', ctypes.c_int*Lighting.MAX_LIGHTS),
    ]

class NPR_LightsGroupsBuffer(object):

    def __init__(self):
        self.data = C_NPR_LightGroupsBuffer()
        self.UBO = UBO()
    
    def load(self, scene):
        for i, light in enumerate(scene.lights):
            self.data.light_group_index[i] = light.parameters['Light Group']

        self.UBO.load_data(self.data)

        for material in scene.materials:
            for shader in material.shader.values():
                if 'MATERIAL_LIGHT_GROUPS' in shader.uniforms.keys():
                    shader.uniforms['MATERIAL_LIGHT_GROUPS'].set_value(material.parameters['Light Groups.Light'])

    def shader_callback(self, shader):
        if 'LIGHT_GROUPS' in shader.uniform_blocks:
            self.UBO.bind(shader.uniform_blocks['LIGHT_GROUPS'])

class C_NPR_LightShadersBuffer(ctypes.Structure):
    _fields_ = [
        ('custom_shading_index', ctypes.c_int*Lighting.MAX_LIGHTS),
    ]

class NPR_LightShaders(object):

    def __init__(self):
        self.data = C_NPR_LightShadersBuffer()
        self.custom_shading_count = 0
        self.UBO = UBO()

        self.texture = None
        self.fbos = None
    
    def load(self, pipeline, depth_texture, scene):
        self.custom_shading_count = 0
        for i, light in enumerate(scene.lights):
            custom_shading_index = -1
            if light.parameters['Shader'] is not None:
                custom_shading_index = self.custom_shading_count
                self.custom_shading_count += 1
            self.data.custom_shading_index[i] = custom_shading_index

        self.UBO.load_data(self.data)

        if self.custom_shading_count == 0:
            return

        lights = [l for l in scene.lights if l.parameters['Shader'] is not None]
        tex = self.texture
        if tex is None or tex.resolution != depth_texture.resolution or tex.length < len(lights):
            self.texture = TextureArray(depth_texture.resolution, len(lights), GL_RGB32F)
            self.fbos = []
            for i in range(len(lights)):
                self.fbos.append(RenderTarget([ArrayLayerTarget(self.texture, i)]))
        
        for i, light in enumerate(lights):
            material = light.parameters['Shader']
            if material.shader and 'SHADER' in material.shader.keys():
                shader = material.shader['SHADER']
                pipeline.common_buffer.bind(shader.uniform_blocks['COMMON_UNIFORMS'])
                pipeline.lights_buffer.bind(shader.uniform_blocks['SCENE_LIGHTS'])
                shader.textures['IN_DEPTH'] = depth_texture
                if 'LIGHT_INDEX' in shader.uniforms:
                    light_index = scene.lights.index(light)
                    print('set light index ', i, light_index)
                    shader.uniforms['LIGHT_INDEX'].set_value(light_index)
                pipeline.draw_screen_pass(shader, self.fbos[i])
    
    def shader_callback(self, shader):
        if 'LIGHTS_CUSTOM_SHADING' in shader.uniform_blocks:
            self.UBO.bind(shader.uniform_blocks['LIGHTS_CUSTOM_SHADING'])
        shader.textures['IN_LIGHT_CUSTOM_SHADING'] = self.texture
        

class NPR_ShadowMaps(ShadowMaps):

    def __init__(self):
        super().__init__()
        self.spot_id_t = None
        self.sun_id_t = None
        self.point_id_t = None
    
    def setup(self, create_fbos=True):
        super().setup(False)
        self.spot_id_t = TextureArray((self.spot_resolution, self.spot_resolution), self.max_spots, 
            GL_R32F, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        self.sun_id_t = TextureArray((self.sun_resolution, self.sun_resolution), self.max_suns, 
            GL_R32F, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        self.point_id_t = CubeMapArray((self.point_resolution, self.point_resolution), self.max_points, 
            GL_R32F, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        
        if create_fbos:
            self.spot_fbos = []
            for i in range(self.spot_depth_t.length):
                self.spot_fbos.append(RenderTarget([ArrayLayerTarget(self.spot_id_t, i)], ArrayLayerTarget(self.spot_depth_t, i)))

            self.sun_fbos = []
            for i in range(self.sun_depth_t.length):
                self.sun_fbos.append(RenderTarget([ArrayLayerTarget(self.sun_id_t, i)], ArrayLayerTarget(self.sun_depth_t, i)))
            
            self.point_fbos = []
            for i in range(self.point_depth_t.length*6):
                self.point_fbos.append(RenderTarget([ArrayLayerTarget(self.point_id_t, i)], ArrayLayerTarget(self.point_depth_t, i)))
    
    def clear(self, spot_count, sun_count, point_count):
        for i in range(spot_count):
            self.spot_fbos[i].clear([0], depth=1)
        for i in range(sun_count):
            self.sun_fbos[i].clear([0], depth=1)
        for i in range(point_count*6):
            self.point_fbos[i].clear([0], depth=1)
    
    def shader_callback(self, shader):
        super().shader_callback(shader)
        shader.textures['SHADOWMAPS_ID_SPOT'] = self.spot_id_t
        shader.textures['SHADOWMAPS_ID_SUN'] = self.sun_id_t
        shader.textures['SHADOWMAPS_ID_POINT'] = self.point_id_t

class NPR_TransparentShadowMaps(NPR_ShadowMaps):

    def __init__(self):
        super().__init__()
        self.spot_color_t = None
        self.sun_color_t = None
        self.point_color_t = None
    
    def setup(self, create_fbos=True):
        super().setup(False)
        self.spot_color_t = TextureArray((self.spot_resolution, self.spot_resolution), self.max_spots, GL_RGB8)
        self.sun_color_t = TextureArray((self.sun_resolution, self.sun_resolution), self.max_suns, GL_RGB8)
        self.point_color_t = CubeMapArray((self.point_resolution, self.point_resolution), self.max_points, GL_RGB8)
        
        if create_fbos:
            self.spot_fbos = []
            for i in range(self.spot_depth_t.length):
                targets = [ArrayLayerTarget(self.spot_id_t, i), ArrayLayerTarget(self.spot_color_t, i)]
                self.spot_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.spot_depth_t, i)))

            self.sun_fbos = []
            for i in range(self.sun_depth_t.length):
                targets = [ArrayLayerTarget(self.sun_id_t, i), ArrayLayerTarget(self.sun_color_t, i)]
                self.sun_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.sun_depth_t, i)))
            
            self.point_fbos = []
            for i in range(self.point_depth_t.length*6):
                targets = [ArrayLayerTarget(self.point_id_t, i), ArrayLayerTarget(self.point_color_t, i)]
                self.point_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.point_depth_t, i)))
    
    def clear(self, spot_count, sun_count, point_count):
        for i in range(spot_count):
            self.spot_fbos[i].clear([0, (0,0,0,0)], depth=1)
        for i in range(sun_count):
            self.sun_fbos[i].clear([0, (0,0,0,0)], depth=1)
        for i in range(point_count*6):
            self.point_fbos[i].clear([0, (0,0,0,0)], depth=1)

    def shader_callback(self, shader):
        shader.textures['TRANSPARENT_SHADOWMAPS_DEPTH_SPOT'] = self.spot_depth_t
        shader.textures['TRANSPARENT_SHADOWMAPS_DEPTH_SUN'] = self.sun_depth_t
        shader.textures['TRANSPARENT_SHADOWMAPS_DEPTH_POINT'] = self.point_depth_t
        shader.textures['TRANSPARENT_SHADOWMAPS_ID_SPOT'] = self.spot_id_t
        shader.textures['TRANSPARENT_SHADOWMAPS_ID_SUN'] = self.sun_id_t
        shader.textures['TRANSPARENT_SHADOWMAPS_ID_POINT'] = self.point_id_t
        shader.textures['TRANSPARENT_SHADOWMAPS_COLOR_SPOT'] = self.spot_color_t
        shader.textures['TRANSPARENT_SHADOWMAPS_COLOR_SUN'] = self.sun_color_t
        shader.textures['TRANSPARENT_SHADOWMAPS_COLOR_POINT'] = self.point_color_t
        

