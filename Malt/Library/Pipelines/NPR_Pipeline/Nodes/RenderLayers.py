from Malt.GL import GL
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type, MaterialParameter

class RenderLayers(PipelineNode):

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
        self.resolution = None
        self.texture_targets = {}
        self.render_target = None
        self.custom_io = []
    
    @staticmethod
    def get_pass_type():
        return 'Render Layer'
    
    @classmethod
    def reflect_inputs(cls):
        inputs = {}
        inputs['Scene'] = Parameter('Scene', Type.OTHER)
        return inputs
    
    @classmethod
    def reflect_outputs(cls):
        outputs = {}
        outputs['Color'] = Parameter('', Type.TEXTURE)
        return outputs
    
    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']
        graph = parameters['PASS_GRAPH']
        custom_io = parameters['CUSTOM_IO']
        scene = inputs['Scene']
        if scene and graph:
            self.draw_layer_count = 0
            self.pipeline.transparency_layers = scene.world_parameters['Transparency.Layers']
            self.transparency_layers = self.pipeline.transparency_layers
            for i in range(self.transparency_layers):
                self.pipeline.draw_layer_count = self.draw_layer_count
                self.pipeline.graphs['Render Layer'].run_source(self.pipeline, graph['source'], graph['parameters'], inputs, outputs)
                self.draw_layer_count += 1
            


NODE = RenderLayers  
