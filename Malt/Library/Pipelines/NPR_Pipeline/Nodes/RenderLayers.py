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
        inputs['Transparent Layers'] = Parameter(2, Type.INT)
        return inputs
    
    @classmethod
    def reflect_outputs(cls):
        outputs = {}
        outputs['Color'] = Parameter('', Type.TEXTURE)
        return outputs
    
    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']
        custom_io = parameters['CUSTOM_IO']
        graph = parameters['PASS_GRAPH']
        scene = inputs['Scene']
        if scene and graph:
            self.layer_index = 0
            self.layer_count = inputs['Transparent Layers'] + 1
            for i in range(self.layer_count):
                graph['parameters']['__LAYER_INDEX__'] = self.layer_index
                graph['parameters']['__LAYER_COUNT__'] = self.layer_count
                self.pipeline.graphs['Render Layer'].run_source(self.pipeline, graph['source'], graph['parameters'], inputs, outputs)
                self.layer_index += 1
            


NODE = RenderLayers  
