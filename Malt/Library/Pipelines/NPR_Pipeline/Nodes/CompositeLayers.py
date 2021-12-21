from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type

class CompositeLayers(PipelineNode):

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
        self.resolution = None
    
    @classmethod
    def reflect_inputs(cls):
        inputs = {}
        inputs['Color'] = Parameter('', Type.TEXTURE)
        return inputs
    
    @classmethod
    def reflect_outputs(cls):
        outputs = {}
        outputs['Color'] = Parameter('', Type.TEXTURE)
        return outputs
    
    def setup_render_targets(self, resolution):
        self.t_opaque_color = Texture(resolution, GL_RGBA16F)
        self.fbo_opaque = RenderTarget([self.t_opaque_color])

        self.t_transparent_color = Texture(resolution, GL_RGBA16F)
        self.fbo_transparent = RenderTarget([self.t_transparent_color])

        self.t_color = Texture(resolution, GL_RGBA16F)
        self.fbo_color = RenderTarget([self.t_color])
    
    def is_opaque_pass(self):
        return self.pipeline.draw_layer_count == 0

    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']

        if self.pipeline.resolution != self.resolution:
            self.setup_render_targets(self.pipeline.resolution)
            self.resolution = self.pipeline.resolution
        
        if inputs['Color']:
            if self.is_opaque_pass():
                self.pipeline.copy_textures(self.fbo_opaque, [inputs['Color']])
                self.fbo_color.clear([(0,0,0,0)])
                self.fbo_transparent.clear([(0,0,0,0)])
            else:
                self.pipeline.blend_transparency_shader.textures['IN_BACK'] = inputs['Color']
                self.pipeline.blend_transparency_shader.textures['IN_FRONT'] = self.t_transparent_color
                self.pipeline.draw_screen_pass(self.pipeline.blend_transparency_shader, self.fbo_color)

                self.pipeline.copy_textures(self.fbo_transparent, [self.t_color])
        
        if self.pipeline.draw_layer_count == self.pipeline.transparency_layers - 1:
            self.pipeline.blend_transparency_shader.textures['IN_BACK'] = self.t_opaque_color
            self.pipeline.blend_transparency_shader.textures['IN_FRONT'] = self.t_transparent_color
            self.pipeline.draw_screen_pass(self.pipeline.blend_transparency_shader, self.fbo_color)

            outputs['Color'] = self.t_color

NODE = CompositeLayers
