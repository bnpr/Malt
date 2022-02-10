from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type

class OpaqueLayer(PipelineNode):

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
    
    @classmethod
    def reflect_inputs(cls):
        return {
            'Output Name' : Parameter('', Type.STRING)
        }
    
    @classmethod
    def reflect_outputs(cls):
        return {
            'Opaque Layer' : Parameter('', Type.TEXTURE)
        }
    
    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']

        output_name = inputs['Output Name']
        render_layers_node = parameters['__GLOBALS__']['__RENDER_LAYERS__']
        outputs['Opaque Layer'] = render_layers_node.opaque_targets.get(output_name)

NODE = OpaqueLayer    
