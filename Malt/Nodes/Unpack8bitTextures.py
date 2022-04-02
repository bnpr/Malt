from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type, MaterialParameter

_UNPACK_SRC = """
#include "Passes/Unpack8bitTextures.glsl"
"""
_UNPACK_SHADER = None

class Unpack8bitTextures(PipelineNode):

    """
    Unpacks up to 4 textures packed into a single one using the *pack_8bit* shader function.  
    *(Useful when a shader needs to output more than 8 textures)*
    """
    
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
    

NODE = Unpack8bitTextures
