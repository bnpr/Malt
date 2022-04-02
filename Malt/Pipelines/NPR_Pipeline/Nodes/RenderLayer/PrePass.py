from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type
from Malt.Scene import TextureShaderResource

from Malt.Pipelines.NPR_Pipeline.NPR_LightShaders import NPR_LightShaders

class PrePass(PipelineNode):
    """
    Renders the scene geometry using the *Mesh Pre Pass*.  
    The node sockets are dynamic, based on the *Pre Pass Custom IO*.  
    If *Normal Depth/ID* is empty, the *PrePass* *Normal Depth/ID* will be used.
    """

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
        self.resolution = None
        self.custom_io = []
        self.npr_light_shaders = NPR_LightShaders()
    
    @staticmethod
    def get_pass_type():
        return 'Mesh.PRE_PASS_PIXEL_SHADER'
    
    @classmethod
    def reflect_inputs(cls):
        inputs = {}
        inputs['Scene'] = Parameter('Scene', Type.OTHER)
        return inputs
    
    @classmethod
    def reflect_outputs(cls):
        outputs = {}
        outputs['Scene'] = Parameter('Scene', Type.OTHER)
        outputs['Normal Depth'] = Parameter('', Type.TEXTURE)
        outputs['ID'] = Parameter('', Type.TEXTURE)
        return outputs
    
    def setup_render_targets(self, resolution, custom_io):
        self.t_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        
        self.t_normal_depth = Texture(resolution, GL_RGBA32F)
        self.t_id = Texture(resolution, GL_RGBA16UI, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        self.custom_targets = {}
        for io in custom_io:
            if io['io'] == 'out' and io['type'] == 'Texture':#TODO
                self.custom_targets[io['name']] = Texture(resolution, GL.GL_RGBA16F)
        self.fbo = RenderTarget([self.t_normal_depth, self.t_id, *self.custom_targets.values()], self.t_depth)
        
        self.t_last_layer_id = Texture(resolution, GL_R16UI, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        self.fbo_last_layer_id = RenderTarget([self.t_last_layer_id])

        self.t_opaque_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        self.fbo_opaque_depth = RenderTarget([], self.t_opaque_depth)
        self.t_transparent_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        self.fbo_transparent_depth = RenderTarget([], self.t_transparent_depth)

    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']
        custom_io = parameters['CUSTOM_IO']
        scene = inputs['Scene']

        is_opaque_pass = parameters['__GLOBALS__']['__LAYER_INDEX__'] == 0

        if self.pipeline.resolution != self.resolution or self.custom_io != custom_io:
            self.setup_render_targets(self.pipeline.resolution, custom_io)
            self.resolution = self.pipeline.resolution
            self.custom_io = custom_io
        
        import copy
        scene = copy.copy(scene)
        opaque_batches, transparent_batches = self.pipeline.get_scene_batches(scene)
        scene.batches = opaque_batches if is_opaque_pass else transparent_batches
        
        shader_resources = scene.shader_resources.copy()
        shader_resources.update({
            'IN_OPAQUE_DEPTH': TextureShaderResource('IN_OPAQUE_DEPTH', self.t_opaque_depth),
            'IN_TRANSPARENT_DEPTH': TextureShaderResource('IN_TRANSPARENT_DEPTH', self.t_transparent_depth),
            'IN_LAST_ID': TextureShaderResource('IN_LAST_ID', self.t_last_layer_id),
        })
        self.fbo.clear([(0,0,1,1), (0,0,0,0)] + [(0,0,0,0)]*len(self.custom_targets), 1)

        self.pipeline.draw_scene_pass(self.fbo, scene.batches, 'PRE_PASS', self.pipeline.default_shader['PRE_PASS'], shader_resources)

        if is_opaque_pass:
            self.fbo_last_layer_id.clear([(0,0,0,0)])
            self.fbo_transparent_depth.clear([], -1)
            self.pipeline.copy_textures(self.fbo_opaque_depth, [], self.t_depth)
        else:
            self.pipeline.copy_textures(self.fbo_last_layer_id, [self.t_id])
            self.pipeline.copy_textures(self.fbo_transparent_depth, [], self.t_depth)

        #CUSTOM LIGHT SHADERS
        self.npr_light_shaders.load(self.pipeline, self.t_depth, scene)

        scene.shader_resources = scene.shader_resources.copy()
        scene.shader_resources.update({
            'LIGHTS_CUSTOM_SHADING': self.npr_light_shaders,
            'IN_NORMAL_DEPTH': TextureShaderResource('IN_NORMAL_DEPTH', self.t_normal_depth),
            'IN_ID': TextureShaderResource('IN_ID', self.t_id),
            'T_DEPTH': TextureShaderResource('', self.t_depth), #just pass the reference
        })

        outputs['Scene'] = scene
        outputs['Normal Depth'] = self.t_normal_depth
        outputs['ID'] = self.t_id
        outputs.update(self.custom_targets)


NODE = PrePass
