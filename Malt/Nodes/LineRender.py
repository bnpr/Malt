from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type

_SHADER = None

class LineRender(PipelineNode):

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
        self.resolution = None
    
    @classmethod
    def reflect_inputs(cls):
        inputs = {}
        inputs['Color'] = Parameter('', Type.TEXTURE)
        inputs['Line Color'] = Parameter('', Type.TEXTURE)
        inputs['Line Width'] = Parameter('', Type.TEXTURE)
        inputs['Max Width'] = Parameter(10, Type.INT)
        inputs['Line Scale'] = Parameter(1.0, Type.FLOAT)
        inputs['Normal Depth'] = Parameter('', Type.TEXTURE)
        inputs['ID'] = Parameter('', Type.TEXTURE)
        return inputs
    
    @classmethod
    def reflect_outputs(cls):
        outputs = {}
        outputs['Color'] = Parameter('', Type.TEXTURE)
        return outputs
    
    def setup_render_targets(self, resolution):
        self.t_color = Texture(resolution, GL_RGBA16F)
        self.fbo_color = RenderTarget([self.t_color])

    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']

        if self.pipeline.resolution != self.resolution:
            self.setup_render_targets(self.pipeline.resolution)
            self.resolution = self.pipeline.resolution
        
        global _SHADER
        if _SHADER is None:
            _SHADER = self.pipeline.compile_shader_from_source('#include "Passes/LineComposite.glsl"')
        
        _SHADER.textures['color_texture'] = inputs['Color']
        _SHADER.textures['depth_texture'] = inputs['Normal Depth']
        _SHADER.uniforms['depth_channel'].set_value(3)
        _SHADER.textures['id_texture'] = inputs['ID']
        _SHADER.textures['line_color_texture'] = inputs['Line Color']
        _SHADER.textures['line_width_texture'] = inputs['Line Width']
        _SHADER.uniforms['line_width_scale'].set_value(inputs['Line Scale'])
        _SHADER.uniforms['brute_force_range'].set_value(inputs['Max Width'])
        
        self.pipeline.draw_screen_pass(_SHADER, self.fbo_color)

        outputs['Color'] = self.t_color

NODE = LineRender    
