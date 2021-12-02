from Malt.GL import GL
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type, MaterialParameter

class ScreenPass(PipelineNode):

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
        self.resolution = None
        self.texture_targets = {}
        self.render_target = None
        self.custom_io = []
    
    @staticmethod
    def get_pass_type():
        return 'Screen Shader'
    
    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']
        material = parameters['PASS_MATERIAL']
        custom_io = parameters['CUSTOM_IO']

        print(custom_io)

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
                        shader.textures[io['name']] = inputs[io['name']]
            self.pipeline.draw_screen_pass(shader, self.render_target)
        
        for io in custom_io:
            if io['io'] == 'out':
                if io['type'] == 'Texture':#TODO
                    outputs[io['name']] = self.texture_targets[io['name']]


NODE = ScreenPass    
