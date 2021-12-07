from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type

class MainPass(PipelineNode):

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
        self.resolution = None
    
    @classmethod
    def get_custom_inputs(cls):
        return {}

    @classmethod
    def get_custom_outputs(cls):
        return {}
    
    @classmethod
    def reflect_inputs(cls):
        inputs = {}
        inputs['PrePass'] = Parameter('PrePass', Type.OTHER)
        inputs['Normal Depth'] = Parameter('', Type.TEXTURE)
        inputs['ID'] = Parameter('', Type.TEXTURE)
        inputs |= {key : Parameter('', Type.TEXTURE) for key in cls.get_custom_inputs().keys()}
        return inputs
    
    @classmethod
    def reflect_outputs(cls):
        outputs = {}
        outputs['Color'] = Parameter('', Type.TEXTURE)
        outputs |= {key : Parameter('', Type.TEXTURE) for key in cls.get_custom_outputs().keys()}
        return outputs
    
    def setup_render_targets(self, resolution, t_depth):
        self.t_custom_outputs = {}
        self.t_main_color = Texture(resolution, GL_RGBA16F)
        fbo_main_targets = [self.t_main_color]
        for key, texture_format in self.get_custom_outputs().items():
            texture = Texture(resolution, texture_format)
            self.t_custom_outputs[key] = texture
            fbo_main_targets.append(texture)
        self.fbo_main = RenderTarget(fbo_main_targets, t_depth)
    
    def is_opaque_pass(self):
        return self.pipeline.draw_layer_count == 0

    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']
        
        pre_pass = inputs['PrePass']
        t_normal_depth = inputs['Normal Depth']
        t_id = inputs['ID']

        if t_normal_depth is None:
            t_normal_depth = pre_pass.t_normal_depth
        if t_id is None:
            t_id = pre_pass.t_id
        
        batches = pre_pass.batches

        if self.pipeline.resolution != self.resolution:
            self.setup_render_targets(self.pipeline.resolution, pre_pass.t_depth)
            self.resolution = self.pipeline.resolution
        
        UBOS = {'COMMON_UNIFORMS' : self.pipeline.common_buffer}
        callbacks = [
            self.pipeline.npr_lighting.shader_callback,
            self.pipeline.npr_light_shaders.shader_callback,
        ]

        textures = {
            'IN_NORMAL_DEPTH': t_normal_depth,
            'IN_ID': t_id,
        }
        clear_colors = [(0)*4]
        clear_colors.extend([(0)*4] * len(self.t_custom_outputs))
        self.fbo_main.clear(clear_colors)
        self.pipeline.draw_scene_pass(self.fbo_main, batches, 'MAIN_PASS', self.pipeline.default_shader['MAIN_PASS'], 
            UBOS, {}, textures, callbacks, GL_EQUAL)

        outputs['Color'] = self.t_main_color
        outputs |= self.t_custom_outputs

NODE = MainPass
