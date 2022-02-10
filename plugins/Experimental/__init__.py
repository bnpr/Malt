import os
from Malt.PipelinePlugin import PipelinePlugin, isinstance_str

class ExperimentalNodes(PipelinePlugin):

    @classmethod
    def poll_pipeline(self, pipeline):
        return isinstance_str(pipeline, 'NPR_Pipeline')
    
    @classmethod
    def register_graph_libraries(self, graphs):
        root = os.path.dirname(__file__)
        graphs['Render Layer'].add_library(os.path.join(root, 'RenderLayer'))

PLUGIN = ExperimentalNodes
