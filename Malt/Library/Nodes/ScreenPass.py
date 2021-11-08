from Malt.GL import GL
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type, MaterialParameter

class ScreenPass(PipelineNode):

    IO_COUNT = 4

    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.resolution = None
        self.texture_targets = [None]*self.IO_COUNT
        self.render_target = None

    @classmethod
    def reflect_inputs(cls):
        inputs = {}
        inputs['Material'] = MaterialParameter('', 'screen')
        for i in range(0, cls.IO_COUNT):
            inputs[f'Input{i}'] = Parameter('', Type.TEXTURE)
        return inputs
    
    @classmethod
    def reflect_outputs(cls):
        outputs = {}
        for i in range(0, cls.IO_COUNT):
            outputs[f'Output{i}'] = Parameter('', Type.TEXTURE)
        return outputs
    
    def execute(self, parameters):
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
