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
    
    @staticmethod
    def get_pass_type():
        return 'Screen Shader'
    
    def execute(self, parameters):
        return
        if self.pipeline.resolution != self.resolution:
            for i in range(self.IO_COUNT):
                self.texture_targets[i] = Texture(self.pipeline.resolution, GL.GL_RGBA16F)
            self.render_target = RenderTarget(self.texture_targets)
            self.resolution = self.pipeline.resolution
        
        self.render_target.clear([(0,0,0,0)]*self.IO_COUNT)

        material = parameters['Material']
        if material and material.shader and 'SHADER' in material.shader:
            shader = material.shader['SHADER']
            for i in range(0, self.IO_COUNT):
                input_name = f'Input{i}'
                texture_name = f'INPUT_{i}'
                shader.textures[texture_name] = parameters[input_name]
            self.pipeline.draw_screen_pass(shader, self.render_target, blend = False)

        for i in range(0, self.IO_COUNT):
            parameters[f'Output{i}'] = self.texture_targets[i]


NODE = ScreenPass    
