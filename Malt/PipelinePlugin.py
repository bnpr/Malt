class PipelinePlugin():

    @classmethod
    def poll_pipeline(self, pipeline):
        return True

    @classmethod
    def register_pipeline_parameters(self, parameters):
        pass

    @classmethod
    def register_pipeline_graphs(self):
        return []

    @classmethod
    def register_graph_libraries(self, graphs):
        pass



