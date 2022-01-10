from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type
from Malt.Scene import TextureShaderResource

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
        inputs['Scene'] = Parameter('Scene', Type.OTHER)
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
        
        scene = inputs['Scene']
        if scene is None:
            return
        t_normal_depth = inputs['Normal Depth']
        t_id = inputs['ID']

        shader_resources = scene.shader_resources.copy()
        if t_normal_depth:
            shader_resources['IN_NORMAL_DEPTH'] = TextureShaderResource('IN_NORMAL_DEPTH', t_normal_depth)
        if t_id:
            shader_resources['IN_ID'] = TextureShaderResource('IN_ID', t_id),
        
        if self.pipeline.resolution != self.resolution or self.custom_io != custom_io:
            t_depth = shader_resources['T_DEPTH'].texture
            self.setup_render_targets(self.pipeline.resolution, t_depth, custom_io)
            self.resolution = self.pipeline.resolution
            self.custom_io = custom_io
        
        for io in custom_io:
            if io['io'] == 'in':
                if io['type'] == 'Texture':#TODO
                    from Malt.SourceTranspiler import GLSLTranspiler
                    glsl_name = GLSLTranspiler.custom_io_reference('IN', 'MAIN_PASS_PIXEL_SHADER', io['name'])
                    shader_resources['CUSTOM_IO'+glsl_name] = TextureShaderResource(glsl_name, inputs[io['name']])
                    
        self.fbo.clear([(0,0,0,0)] * len(self.fbo.targets))
        self.pipeline.draw_scene_pass(self.fbo, scene.batches, 'MAIN_PASS', self.pipeline.default_shader['MAIN_PASS'], 
            shader_resources, GL_EQUAL)

        outputs.update(self.custom_targets)

NODE = MainPass
