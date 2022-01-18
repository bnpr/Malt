import os
from Malt.PipelinePlugin import PipelinePlugin, isinstance_str

class PluginExample(PipelinePlugin):

    @classmethod
    def poll_pipeline(self, pipeline):
        return isinstance_str(pipeline, 'NPR_Pipeline')
    
    @classmethod
    def register_graph_libraries(self, graphs):
        library_path = os.path.join(os.path.dirname(__file__), 'Shaders')
        for graph in graphs.values():
            if graph.language == 'GLSL':
                graph.add_library(library_path)

PLUGIN = PluginExample
