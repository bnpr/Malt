# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import math

from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget

import Malt.Pipeline

_shader_src = '''
#include "Passes/JumpFlood.glsl"
'''

_line_cleanup_src = '''
#include "Passes/LineCleanUp.glsl"
'''

_line_composite_src = '''
#include "Passes/LineComposite.glsl"
'''

_LINE_COMPOSITE_SHADER = None

class LineRendering(object):

    def __init__(self):
        '''
        self.t_a = None
        self.t_b = None
        self.fbo_a = None
        self.fbo_b = None
        self.shader = None
        self.cleanup_shader = None
        '''
        self.t_composite = None
        self.fbo_composite = None
        self.composite_shader = None

    def composite_line(self, max_width, pipeline, common_buffer, color, depth, id_texture, line_color, line_data):
        '''
        if self.t_a is None or self.t_a.resolution != color.resolution:
            self.t_a = Texture(color.resolution, GL_RGBA32F)
            self.fbo_a = RenderTarget([self.t_a])
            self.t_b = Texture(color.resolution, GL_RGBA32F)
            self.fbo_b = RenderTarget([self.t_b])
        if self.shader is None:
            self.shader = pipeline.compile_shader_from_source(_shader_src)
            self.cleanup_shader = pipeline.compile_shader_from_source(_line_cleanup_src)
        
        #CLEANUP LINE
        #(Try to workaround numerical stability issues, disabled for now)
        cleanup = False
        if cleanup:
            self.fbo_composite.clear([(0,0,0,0)])
            self.cleanup_shader.textures['line_data_texture'] = line_data
            self.cleanup_shader.bind()
            common_buffer.bind(self.cleanup_shader.uniform_blocks['COMMON_UNIFORMS'])
            pipeline.draw_screen_pass(self.cleanup_shader, self.fbo_composite)
            line_data = self.fbo_composite.targets[0]
        
        #JUMP FLOOD
        #Disabled since we moved back to brute-force line rendering
        jump_flood = False
        if jump_flood:
            jump_flood_max_width = max(line_data.resolution[0], line_data.resolution[1])
            
            steps = []
            width = 1
            while width < jump_flood_max_width:
                steps.append(width)
                width*=2
            
            steps.reverse()
            
            self.fbo_a.clear([(-1,-1,-1,-1)])
            self.fbo_b.clear([(-1,-1,-1,-1)])
            read = line_data
            write = self.fbo_b

            for i, step in enumerate(steps):
                if i > 0:
                    if i % 2 == 0:
                        read = self.t_a
                        write = self.fbo_b
                    else:
                        read = self.t_b
                        write = self.fbo_a
                
                self.shader.textures['input_texture'] = read
                self.shader.uniforms['width'].set_value(step)
                self.shader.bind()
                common_buffer.bind(self.shader.uniform_blocks['COMMON_UNIFORMS'])
                pipeline.draw_screen_pass(self.shader, write)
        '''

        if self.t_composite is None or self.t_composite.resolution != color.resolution:
            self.t_composite = Texture(color.resolution, GL_RGBA32F)
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
        #self.composite_shader.textures['line_distance_field_texture'] = write.targets[0]
        self.composite_shader.bind()
        common_buffer.bind(self.composite_shader.uniform_blocks['COMMON_UNIFORMS'])
        pipeline.draw_screen_pass(self.composite_shader, self.fbo_composite)
        
        return self.t_composite



            
        

