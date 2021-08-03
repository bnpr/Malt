
class PipelineNode():

    def __init__(self, pipeline):
        self.pipeline = pipeline
    
    @staticmethod
    def static_reflect(name, inputs, outputs):
        dictionary = {
            'name' : name,
            'type' : 'void',
            'file' : 'Render',
            'parameters' : []
        }
        for name, input in inputs.items():
            dictionary['parameters'].append({
                'name' : name,
                'type' : input,
                'size' : input.size,
                'io' : 'in',
            })
        for name, output in outputs.items():
            dictionary['parameters'].append({
                'name' : name,
                'type' : output,
                'size' : output.size,
                'io' : 'out',
            })
        return dictionary
    
    @classmethod
    def reflect(cls):
        return cls.static_reflect(cls.__name__, cls.reflect_inputs(), cls.reflect_outputs())

    @classmethod
    def reflect_inputs(cls):
        return {}

    @classmethod
    def reflect_outputs(cls):
        return {}
    
    def execute(self, parameters):
        pass
    
from Malt.Parameter import Parameter, Type, MaterialParameter

class RenderScreen(PipelineNode):

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
        from Malt.GL import GL
        from Malt.GL.Texture import Texture
        from Malt.GL.RenderTarget import RenderTarget

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
    
_UNPACK_SRC = """
#include "Passes/Unpack8bitTextures.glsl"
"""
_UNPACK_SHADER = None

class Unpack8bitTextures(PipelineNode):
    
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.resolution = None
        self.texture_targets = [None]*4
        self.render_target = None

    @classmethod
    def reflect_inputs(cls):
        return {
            'Packed Texture' : Parameter('usampler2D', Type.OTHER)
        }
    
    @classmethod
    def reflect_outputs(cls):
        return {
            'A' : Parameter('', Type.TEXTURE),
            'B' : Parameter('', Type.TEXTURE),
            'C' : Parameter('', Type.TEXTURE),
            'D' : Parameter('', Type.TEXTURE),
        }
    
    def execute(self, parameters):
        from Malt.GL import GL
        from Malt.GL.Texture import Texture
        from Malt.GL.RenderTarget import RenderTarget

        if self.pipeline.resolution != self.resolution:
            for i in range(4):
                #TODO: Doesn't work with GL_RGBA?
                self.texture_targets[i] = Texture(self.pipeline.resolution, GL.GL_RGBA16F)
            self.render_target = RenderTarget(self.texture_targets)
            self.resolution = self.pipeline.resolution
        
        self.render_target.clear([(0,0,0,0)]*4)

        global _UNPACK_SHADER
        if _UNPACK_SHADER is None:
            _UNPACK_SHADER = self.pipeline.compile_shader_from_source(_UNPACK_SRC)

        _UNPACK_SHADER.textures['IN_PACKED'] = parameters['Packed Texture']
        self.pipeline.draw_screen_pass(_UNPACK_SHADER, self.render_target, blend = False)

        parameters['A'] = self.texture_targets[0]
        parameters['B'] = self.texture_targets[1]
        parameters['C'] = self.texture_targets[2]
        parameters['D'] = self.texture_targets[3]
    

