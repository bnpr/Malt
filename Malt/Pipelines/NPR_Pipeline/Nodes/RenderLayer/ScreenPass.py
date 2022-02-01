from Malt.GL import GL
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type
from Malt.Scene import TextureShaderResource


class ScreenPass(PipelineNode):

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
        self.resolution = None
        self.texture_targets = {}
        self.render_target = None
        self.custom_io = []
    
    @staticmethod
    def get_pass_type():
        return 'Screen.SCREEN_SHADER'
    
    @classmethod
    def reflect_inputs(cls):
        inputs = {}
        inputs['Layer Only'] = Parameter(True, Type.BOOL)
        inputs['Scene'] = Parameter('Scene', Type.OTHER)
        inputs['Normal Depth'] = Parameter('', Type.TEXTURE)
        inputs['ID'] = Parameter('', Type.TEXTURE)
        return inputs
    
    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']
        material = parameters['PASS_MATERIAL']
        custom_io = parameters['CUSTOM_IO']

        deferred_mode = inputs['Layer Only']
        scene = inputs['Scene']
        t_normal_depth = inputs['Normal Depth']
        t_id = inputs['ID']

        shader_resources = {}
        if scene:
            shader_resources = scene.shader_resources.copy()
        if t_normal_depth:
            shader_resources['IN_NORMAL_DEPTH'] = TextureShaderResource('IN_NORMAL_DEPTH', t_normal_depth)
        if t_id:
            shader_resources['IN_ID'] = TextureShaderResource('IN_ID', t_id)

        if self.pipeline.resolution != self.resolution or self.custom_io != custom_io:
            self.texture_targets = {}
            for io in custom_io:
                if io['io'] == 'out':
                    if io['type'] == 'Texture':#TODO
                        self.texture_targets[io['name']] = Texture(self.pipeline.resolution, GL.GL_RGBA16F)
            self.render_target = RenderTarget([*self.texture_targets.values()])
            self.resolution = self.pipeline.resolution
            self.custom_io = custom_io
        
        self.render_target.clear([(0,0,0,0)]*len(self.texture_targets))

        if material and material.shader and 'SHADER' in material.shader:
            shader = material.shader['SHADER']
            for io in custom_io:
                if io['io'] == 'in':
                    if io['type'] == 'Texture':#TODO
                        from Malt.SourceTranspiler import GLSLTranspiler
                        glsl_name = GLSLTranspiler.custom_io_reference('IN', 'SCREEN_SHADER', io['name'])
                        shader.textures[glsl_name] = inputs[io['name']]
            self.pipeline.common_buffer.bind(shader.uniform_blocks['COMMON_UNIFORMS'])
            for resource in shader_resources.values():
                resource.shader_callback(shader)
            shader.uniforms['RENDER_LAYER_MODE'].set_value(True)
            shader.uniforms['DEFERRED_MODE'].set_value(deferred_mode)
            self.pipeline.draw_screen_pass(shader, self.render_target)
        
        for io in custom_io:
            if io['io'] == 'out':
                if io['type'] == 'Texture':#TODO
                    outputs[io['name']] = self.texture_targets[io['name']]


NODE = ScreenPass    
