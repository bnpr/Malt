from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type

class MainPass(PipelineNode):

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
        self.resolution = None
    
    @staticmethod
    def get_pass_type():
        return 'Mesh.MAIN_PASS_PIXEL_SHADER'
    
    @classmethod
    def reflect_inputs(cls):
        inputs = {}
        inputs['PrePass'] = Parameter('PrePass', Type.OTHER)
        inputs['Normal Depth'] = Parameter('', Type.TEXTURE)
        inputs['ID'] = Parameter('', Type.TEXTURE)
        return inputs
    
    @classmethod
    def reflect_outputs(cls):
        outputs = {}
        return outputs
    
    def setup_render_targets(self, resolution, t_depth, custom_io):
        self.custom_targets = {}
        for io in custom_io:
            if io['io'] == 'out' and io['type'] == 'Texture':#TODO
                self.custom_targets[io['name']] = Texture(resolution, GL.GL_RGBA16F)
        self.fbo = RenderTarget([*self.custom_targets.values()], t_depth)

    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']
        custom_io = parameters['CUSTOM_IO']
        
        pre_pass = inputs['PrePass']
        t_normal_depth = inputs['Normal Depth']
        t_id = inputs['ID']

        if t_normal_depth is None:
            t_normal_depth = pre_pass.t_normal_depth
        if t_id is None:
            t_id = pre_pass.t_id
        
        batches = pre_pass.batches

        if self.pipeline.resolution != self.resolution or self.custom_io != custom_io:
            self.setup_render_targets(self.pipeline.resolution, pre_pass.t_depth, custom_io)
            self.resolution = self.pipeline.resolution
            self.custom_io = custom_io
        
        UBOS = {'COMMON_UNIFORMS' : self.pipeline.common_buffer}
        callbacks = [
            self.pipeline.npr_lighting.shader_callback,
            self.pipeline.npr_light_shaders.shader_callback,
        ]

        textures = {
            'IN_NORMAL_DEPTH': t_normal_depth,
            'IN_ID': t_id,
        }
        self.fbo.clear([(0,0,0,0)] * len(self.fbo.targets))
        self.pipeline.draw_scene_pass(self.fbo, batches, 'MAIN_PASS', self.pipeline.default_shader['MAIN_PASS'], 
            UBOS, {}, textures, callbacks, GL_EQUAL)

        outputs.update(self.custom_targets)

NODE = MainPass
