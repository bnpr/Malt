# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

from Malt.GL import *

from Malt.Texture import Texture
from Malt.RenderTarget import RenderTarget

_shader_src='''
#version 410 core
#extension GL_ARB_shading_language_include : enable

#include "Passes/DepthToBlenderDepth.glsl"
'''

class CompositeDepth(object):
    
    def __init__(self):
        self.t = None
        self.fbo = None

        self.shader = None
    
    def render(self, pipeline, common_buffer, depth_texture):
        if self.t is None or self.t.resolution != depth_texture.resolution:
            self.t = Texture(depth_texture.resolution, GL_R32F)
            self.fbo = RenderTarget([self.t])
        
        if self.shader == None:
            self.shader = pipeline.compile_shader_from_source(_shader_src)
        
        self.shader.textures['DEPTH_TEXTURE'] = depth_texture
        self.shader.bind()
        common_buffer.bind(self.shader.uniform_blocks['COMMON_UNIFORMS'])
        pipeline.draw_screen_pass(self.shader, self.fbo)
        return self.t

        



