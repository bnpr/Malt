# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

from os import path

from Malt.GL import *
from Malt.Pipeline import *
from Malt.Mesh import Mesh
from Malt.Shader import Shader
from Malt.Texture import Texture
from Malt.RenderTarget import RenderTarget
from Malt.Parameter import Parameter
from Malt.UBO import UBO

from Malt.Render import Common
from Malt.Render import DepthToCompositeDepth
from Malt.Render import Lighting
from Malt.Render import Line
from Malt.Render import Sampling


_NPR_Pipeline_Common='''
#version 410 core
#extension GL_ARB_shading_language_include : enable

#include "Pipelines/NPR_Pipeline.glsl"
'''

_DEFAULT_SHADER = None

class PipelineTest(Pipeline):

    def __init__(self):
        super().__init__()

        self.sampling_grid_size = 2

        self.parameters.world['Background Color'] = Parameter((0.5,0.5,0.5,1), Type.FLOAT, 4)
        self.parameters.scene['Line Width Max'] = Parameter(10, Type.INT)
        self.parameters.scene['Samples Grid Size Preview'] = Parameter(4, Type.INT)
        self.parameters.scene['Samples Grid Size Render'] = Parameter(8, Type.INT)
        self.parameters.scene['Samples Width'] = Parameter(1.5, Type.FLOAT)
        self.parameters.scene['Shadow Cascades Distribution Exponent'] = Parameter(21, Type.INT)
        self.parameters.scene['ShadowMaps Spot Resolution'] = Parameter(2048, Type.INT)
        self.parameters.scene['ShadowMaps Sun Resolution'] = Parameter(2048, Type.INT)
        self.parameters.scene['ShadowMaps Point Resolution'] = Parameter(2048, Type.INT)

        global _DEFAULT_SHADER
        if _DEFAULT_SHADER is None: _DEFAULT_SHADER = self.compile_material_from_source('mesh','')
        self.default_shader = _DEFAULT_SHADER

        self.common_buffer = Common.CommonBuffer()
        self.lights_buffer = Lighting.get_lights_buffer()

        self.line_rendering = Line.LineRendering()

        self.composite_depth = DepthToCompositeDepth.CompositeDepth()

    def compile_material_from_source(self, material_type, source, include_paths=[]):
        if material_type == 'mesh':
            source = _NPR_Pipeline_Common + source
            return {
                'PRE_PASS' : self.compile_shader_from_source(
                    source, 'COMMON_VERTEX_SHADER', 'PRE_PASS_PIXEL_SHADER', include_paths, ['PRE_PASS']
                ),
                'MAIN_PASS' : self.compile_shader_from_source(
                    source, 'COMMON_VERTEX_SHADER', 'MAIN_PASS_PIXEL_SHADER', include_paths, ['MAIN_PASS']
                )
            }
        elif material_type == 'screen':
            return {
                'SHADER' : self.compile_shader_from_source(source, None, None, include_paths)
            }
    
    def setup_render_targets(self, resolution):
        self.t_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        
        self.t_prepass_normal_depth = Texture(resolution, GL_RGBA32F)
        self.t_prepass_id = Texture(resolution, GL_R32F)
        self.fbo_prepass = RenderTarget([self.t_prepass_normal_depth, self.t_prepass_id], self.t_depth)
        
        self.t_main_color = Texture(resolution, GL_RGB32F)
        self.t_line_color = Texture(resolution, GL_RGB32F)
        self.t_line_data = Texture(resolution, GL_RGB32F)
        self.fbo_main = RenderTarget([self.t_main_color, self.t_line_color, self.t_line_data], self.t_depth)

        self.t_color_accumulate = Texture(resolution, GL_RGB32F)
        self.fbo_accumulate = RenderTarget([self.t_color_accumulate])
    
    def get_samples(self, width=1.0):
        return Sampling.get_RGSS_samples(self.sampling_grid_size, width)
    
    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        #SETUP SAMPLING
        if is_final_render:
            self.sampling_grid_size = scene.parameters['Samples Grid Size Render']
        else:
            self.sampling_grid_size = scene.parameters['Samples Grid Size Preview']

        sample_offset = self.get_samples(scene.parameters['Samples Width'])[self.sample_count]

        #SETUP PER-OBJECT PARAMETERS
        for i, obj in enumerate(scene.objects):
            obj.parameters['MODEL'] = obj.matrix
            obj.parameters['ID'] = i+1
        
        #SETUP UNIFORM BLOCKS
        self.common_buffer.load(scene, resolution, sample_offset, self.sample_count)
        self.lights_buffer.load(scene, self, 'PRE_PASS', 
            scene.parameters['Shadow Cascades Distribution Exponent'],
            scene.parameters['ShadowMaps Spot Resolution'],
            scene.parameters['ShadowMaps Sun Resolution'],
            scene.parameters['ShadowMaps Point Resolution'])

        UBOS = {
            'COMMON_UNIFORMS' : self.common_buffer,
            'SCENE_LIGHTS' : self.lights_buffer
        }

        #PRE-PASS
        self.fbo_prepass.clear([(0,0,1,1), (0,0,0,0)], 1, 0)
        self.draw_scene_pass(self.fbo_prepass, scene.objects, 'PRE_PASS', self.default_shader['PRE_PASS'], UBOS)

        #MAIN-PASS
        textures = {
            'IN_NORMAL_DEPTH': self.t_prepass_normal_depth,
            'IN_ID': self.t_prepass_id,
        }
        callbacks = [
            lambda shader : self.lights_buffer.shader_callback(shader)
        ]
        self.fbo_main.clear([scene.world_parameters['Background Color'], (0,0,0,0), (-1,-1,-1,-1)])
        self.draw_scene_pass(self.fbo_main, scene.objects, 'MAIN_PASS', self.default_shader['MAIN_PASS'], UBOS, {}, textures, callbacks)        
        
        #COMPOSITE LINE
        composited_line = self.line_rendering.composite_line(
            scene.parameters['Line Width Max'], self, self.common_buffer, 
            self.t_main_color, self.t_depth, self.t_prepass_id, self.t_line_color, self.t_line_data)

        # TEMPORAL SUPER-SAMPLING ACCUMULATION
        self.blend_texture(composited_line, self.fbo_accumulate, 1.0 / (self.sample_count + 1))

        #COMPOSITE DEPTH
        composite_depth = None
        if is_final_render:
            composite_depth = self.composite_depth.render(self, self.common_buffer, self.t_depth)

        return {
            'COLOR' : self.t_color_accumulate,
            'DEPTH' : composite_depth,
        }

