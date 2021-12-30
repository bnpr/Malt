# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget

_shader_src='''
#include "Passes/DepthToBlenderDepth.glsl"
'''

_SHADER = None

class CompositeDepth():
    
    def __init__(self):
        self.t = None
        self.fbo = None

        self.shader = None
    
    def render(self, pipeline, common_buffer, depth_texture, depth_channel=0):
        if self.t is None or self.t.resolution != depth_texture.resolution:
            self.t = Texture(depth_texture.resolution, GL_R32F)
            self.fbo = RenderTarget([self.t])
        
        if self.shader == None:
            global _SHADER
            if _SHADER is None: _SHADER = pipeline.compile_shader_from_source(_shader_src)
            self.shader = _SHADER
        
        self.shader.textures['DEPTH_TEXTURE'] = depth_texture
        self.shader.uniforms['DEPTH_CHANNEL'].set_value(depth_channel)
        self.shader.bind()
        common_buffer.bind(self.shader.uniform_blocks['COMMON_UNIFORMS'])
        pipeline.draw_screen_pass(self.shader, self.fbo)
        return self.t

        



