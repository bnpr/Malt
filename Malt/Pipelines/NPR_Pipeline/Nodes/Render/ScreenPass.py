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
    
    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']
        material = parameters['PASS_MATERIAL']
        custom_io = parameters['CUSTOM_IO']

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
            self.pipeline.common_buffer.shader_callback(shader)
            shader.uniforms['RENDER_LAYER_MODE'].set_value(False)
            self.pipeline.draw_screen_pass(shader, self.render_target)
        
        for io in custom_io:
            if io['io'] == 'out':
                if io['type'] == 'Texture':#TODO
                    outputs[io['name']] = self.texture_targets[io['name']]


NODE = ScreenPass    
