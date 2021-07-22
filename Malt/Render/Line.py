# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import math

from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget

_line_composite_src = '''
#include "Passes/LineComposite.glsl"
'''

_LINE_COMPOSITE_SHADER = None

class LineRendering(object):

    def __init__(self):
        self.t_composite = None
        self.fbo_composite = None
        self.composite_shader = None

    def composite_line(self, max_width, pipeline, common_buffer, color, depth, id_texture, line_color, line_data):
        if self.t_composite is None or self.t_composite.resolution != color.resolution:
            self.t_composite = Texture(color.resolution, GL_RGBA16F)
            self.fbo_composite = RenderTarget([self.t_composite])
        
        if self.composite_shader is None:
            global _LINE_COMPOSITE_SHADER
            if _LINE_COMPOSITE_SHADER is None: _LINE_COMPOSITE_SHADER = pipeline.compile_shader_from_source(_line_composite_src)
            self.composite_shader = _LINE_COMPOSITE_SHADER

        #LINE COMPOSITE
        self.fbo_composite.clear([(0,0,0,0)])
        self.composite_shader.uniforms['brute_force_range'].set_value(math.ceil(max_width / 2))
        self.composite_shader.textures['color_texture'] = color
        self.composite_shader.textures['depth_texture'] = depth
        self.composite_shader.textures['id_texture'] = id_texture
        self.composite_shader.textures['line_color_texture'] = line_color
        self.composite_shader.textures['line_data_texture'] = line_data
        self.composite_shader.bind()
        common_buffer.bind(self.composite_shader.uniform_blocks['COMMON_UNIFORMS'])
        pipeline.draw_screen_pass(self.composite_shader, self.fbo_composite)
        
        return self.t_composite



            
        

