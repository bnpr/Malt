# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

import math

from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type, MaterialParameter

_line_composite_src = '''
#include "Passes/LineComposite.glsl"
'''

_LINE_COMPOSITE_SHADER = None

class LineComposite(PipelineNode):

    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.resolution = None
        self.t_composite = None
        self.fbo_composite = None
        global _LINE_COMPOSITE_SHADER
        if _LINE_COMPOSITE_SHADER is None: 
            _LINE_COMPOSITE_SHADER = pipeline.compile_shader_from_source(_line_composite_src)
        self.composite_shader = _LINE_COMPOSITE_SHADER
    
    @classmethod
    def reflect_inputs(cls):
        inputs = {}
        inputs['Max Width'] = Parameter(10, Type.INT)
        inputs['Color'] = Parameter('', Type.TEXTURE)
        inputs['Depth'] = Parameter('', Type.TEXTURE)
        inputs['ID'] = Parameter('', Type.TEXTURE)
        inputs['Line Color'] = Parameter('', Type.TEXTURE)
        inputs['Line Width'] = Parameter('', Type.TEXTURE)
        return inputs
    
    @classmethod
    def reflect_outputs(cls):
        outputs = {}
        outputs['Result'] = Parameter('', Type.TEXTURE)
        return outputs

    def execute(self, parameters):
        if self.pipeline.resolution != self.resolution:
            self.t_composite = Texture(self.pipeline.resolution, GL_RGBA16F)
            self.fbo_composite = RenderTarget([self.t_composite])
        
        #LINE COMPOSITE
        self.fbo_composite.clear([(0,0,0,0)])
        self.composite_shader.uniforms['brute_force_range'].set_value(math.ceil(parameters['Max Width'] / 2))
        self.composite_shader.textures['color_texture'] = parameters['Color']
        self.composite_shader.textures['depth_texture'] = parameters['Depth']
        self.composite_shader.textures['id_texture'] = parameters['ID']
        self.composite_shader.textures['line_color_texture'] = parameters['Line Color']
        self.composite_shader.textures['line_data_texture'] = parameters['Line Width']
        self.composite_shader.bind()
        self.pipeline.common_buffer.bind(self.composite_shader.uniform_blocks['COMMON_UNIFORMS'])
        self.pipeline.draw_screen_pass(self.composite_shader, self.fbo_composite)
        
        parameters['Result'] = self.t_composite


NODE = LineComposite
