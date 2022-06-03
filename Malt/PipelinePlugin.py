from Malt.Utils import isinstance_str

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

    @classmethod
    def blendermalt_register(self):
        pass

    @classmethod
    def blendermalt_unregister(self):
        pass

def load_plugins_from_dir(dir):
    import sys, os, importlib
    if dir not in sys.path:
        sys.path.append(dir)
    plugins=[]
    for e in os.scandir(dir):
        if (e.path.startswith('.') or e.path.startswith('_') or 
            e.is_file() and e.path.endswith('.py') == False):
            continue
        try:
            '''
            spec = importlib.util.spec_from_file_location("_dynamic_plugin_module_", e.path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            '''
            module = importlib.import_module(e.name)
            importlib.reload(module)
            plugins.append(module.PLUGIN)
        except:
            import traceback
            traceback.print_exc()
            print('FILEPATH : ', e.path)
    return plugins
