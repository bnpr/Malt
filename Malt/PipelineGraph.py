class PipelineGraph(object):
    
    def __init__(self, language, file_extension, functions, structs, graph_IO):
        self.language = language
        self.file_extension = file_extension
        self.functions = functions
        self.structs = structs
        self.graph_IO = graph_IO
    
    def generate_source(self, parameters):
        return ''
    
    def get_serializable_copy(self):
        from copy import copy
        return copy(self)

class GLSLPipelineGraph(PipelineGraph):

    def __init__(self, file_extension, source, root_path, graph_io_map, default_global_scope):
        from . GL.Shader import glsl_reflection
        reflection = glsl_reflection(source, root_path)
        functions = reflection["functions"]
        structs = reflection["structs"]
        graph_io = {}
        for name in graph_io_map.keys():
            graph_io[name] = functions[name]        
        for key in [*functions.keys()]:
            name = functions[key]['name']
            if name.startswith('_') or name.isupper() or name == 'main':
                functions.pop(key)
        for name in [*structs.keys()]:
            if name.startswith('_'):
                structs.pop(name)
        super().__init__('GLSL', file_extension, functions, structs, graph_io)
        self.graph_io_map = graph_io_map
        self.default_global_scope = default_global_scope
    
    def generate_source(self, parameters):
        import textwrap
        code = ''
        for graph_function, (define, declaration) in self.graph_io_map.items():
            if graph_function in parameters.keys() and define:
                code += '#define {}\n'.format(define)
        code += '\n\n' + self.default_global_scope + '\n\n' + parameters['GLOBAL'] + '\n\n'
        for graph_function, (define, declaration) in self.graph_io_map.items():
            if graph_function in parameters.keys():
                code += '{}\n{{\n{}\n}}'.format(declaration, textwrap.indent(parameters[graph_function],'\t'))
        code += '\n\n'
        return code

class PythonPipelineGraph(PipelineGraph):
    
    def __init__(self, pipeline, function_nodes, graph_io_reflection):
        self.pipeline = pipeline
        self.node_instances = {}
        self.nodes = {}
        functions = {}
        for node_class in function_nodes:
            reflection = node_class.reflect()
            functions[reflection['name']] = reflection
            self.nodes[reflection['name']] = node_class
        graph_io = {}
        for node in graph_io_reflection:
            graph_io[node['name']] = node
        super().__init__('Python', '-render_layer.py', functions, {}, graph_io)
    
    def generate_source(self, parameters):
        src = ''
        for io in self.graph_IO.keys():
            if io in parameters.keys():
                src += parameters[io]
        return src
    
    def get_serializable_copy(self):
        from copy import copy
        result = copy(self)
        result.pipeline = None
        result.nodes = None
        return result
    
    def run_source(self, source, PARAMETERS, IN, OUT):
        try:
            def run_node(node_name, node_type, parameters):
                if node_name not in self.node_instances.keys():
                    node_class = self.nodes[node_type]
                    self.node_instances[node_name] = node_class(self.pipeline)
                self.node_instances[node_name].execute(parameters)
            exec(source)
        except:
            import traceback
            traceback.print_exc()
            print(source)
