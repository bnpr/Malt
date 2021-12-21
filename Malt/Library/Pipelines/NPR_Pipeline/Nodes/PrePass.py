from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type

class PrePass(PipelineNode):

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
        self.resolution = None
        self.batches = None
    
    @classmethod
    def reflect_inputs(cls):
        inputs = {}
        inputs['Scene'] = Parameter('Scene', Type.OTHER)
        return inputs
    
    @classmethod
    def reflect_outputs(cls):
        outputs = {}
        outputs['PrePass'] = Parameter('PrePass', Type.OTHER)
        outputs['Normal Depth'] = Parameter('', Type.TEXTURE)
        outputs['ID'] = Parameter('', Type.TEXTURE)
        return outputs
    
    def setup_render_targets(self, resolution):
        self.t_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        
        self.t_normal_depth = Texture(resolution, GL_RGBA32F)
        self.t_id = Texture(resolution, GL_RGBA16UI, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        self.fbo = RenderTarget([self.t_normal_depth, self.t_id], self.t_depth)
        
        self.t_last_layer_id = Texture(resolution, GL_R16UI, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        self.fbo_last_layer_id = RenderTarget([self.t_last_layer_id])

        self.t_opaque_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        self.fbo_opaque_depth = RenderTarget([], self.t_opaque_depth)
        self.t_transparent_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        self.fbo_transparent_depth = RenderTarget([], self.t_transparent_depth)
    
    def is_opaque_pass(self):
        return self.pipeline.draw_layer_count == 0

    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']
        scene = inputs['Scene']

        if self.pipeline.resolution != self.resolution:
            self.setup_render_targets(self.pipeline.resolution)
            self.resolution = self.pipeline.resolution
        
        opaque_batches, transparent_batches = self.pipeline.get_scene_batches(scene)
        self.batches = opaque_batches if self.is_opaque_pass() else transparent_batches
        
        UBOS = {'COMMON_UNIFORMS' : self.pipeline.common_buffer}
        callbacks = [self.pipeline.npr_lighting.shader_callback]

        textures = {
            'IN_OPAQUE_DEPTH': self.t_opaque_depth,
            'IN_TRANSPARENT_DEPTH': self.t_transparent_depth,
            'IN_LAST_ID': self.t_last_layer_id,
        }
        self.fbo.clear([(0,0,1,1), (0,0,0,0)], 1)

        self.pipeline.draw_scene_pass(self.fbo, self.batches, 'PRE_PASS', self.pipeline.default_shader['PRE_PASS'],
            UBOS, {}, textures, callbacks)

        if self.is_opaque_pass():
            self.fbo_last_layer_id.clear([(0,0,0,0)])
            self.fbo_transparent_depth.clear([], -1)
            self.pipeline.copy_textures(self.fbo_opaque_depth, [], self.t_depth)
        else:
            self.pipeline.copy_textures(self.fbo_last_layer_id, [self.t_id])
            self.pipeline.copy_textures(self.fbo_transparent_depth, [], self.t_depth)

        #CUSTOM LIGHT SHADERS
        self.pipeline.npr_light_shaders.load(self.pipeline, self.t_depth, scene, self.pipeline.npr_lighting.lights_buffer)

        outputs['PrePass'] = self
        outputs['Normal Depth'] = self.t_normal_depth
        outputs['ID'] = self.t_id

NODE = PrePass
