class PipelineGraph():

    INTERNAL_PASS = 0
    GLOBAL_PASS = 1
    SCENE_PASS = 2
    
    def __init__(self, language, file_extension, pass_type, functions, structs, graph_IO):
        self.language = language
        self.file_extension = file_extension
        self.pass_type = pass_type
        self.functions = functions
        self.structs = structs
        self.graph_IO = graph_IO
        for key in [*functions.keys()]:
            name = functions[key]['name']
            if name.startswith('_') or name.isupper() or name == 'main':
                functions.pop(key)
        for name in [*structs.keys()]:
            if name.startswith('_'):
                structs.pop(name)
    
    def generate_source(self, parameters):
        return ''
    
    def get_serializable_copy(self):
        from copy import copy
        return copy(self)


class GLSLGraphIO():

    COMMON_INPUT_TYPES = ['sampler2D', 'usampler2D', 'isampler2D']
    COMMON_OUTPUT_TYPES = [
        'float','vec2','vec3','vec4',
        'uint','uvec2','uvec3','uvec4',
        'int','ivec2','ivec3','ivec4',
    ]
    
    def __init__(self, name, define = None, dynamic_input_types = [], dynamic_output_types = []):
        self.name = name
        self.define = define
        self.dynamic_input_types = dynamic_input_types
        self.dynamic_output_types = dynamic_output_types
        self.signature = None
        self.function = None

class GLSLPipelineGraph(PipelineGraph):

    def __init__(self, pass_type, file_extension, root_path, source, default_global_scope, graph_io):
        from . GL.Shader import glsl_reflection
        reflection = glsl_reflection(source, root_path)
        functions = reflection["functions"]
        structs = reflection["structs"]
        graph_io_map = {}
        for io in graph_io:
            io.function = functions[io.name]
            io.signature = io.function['signature']
            graph_io_map[io.name] = io
        self.default_global_scope = default_global_scope
        super().__init__('GLSL', file_extension, pass_type, functions, structs, graph_io_map)
    
    def generate_source(self, parameters):
        import textwrap
        code = ''
        for graph_IO in self.graph_IO.values():
            if graph_IO.name in parameters.keys() and graph_IO.define:
                code += '#define {}\n'.format(graph_IO.define)
        code += '\n\n' + self.default_global_scope + '\n\n' + parameters['GLOBAL'] + '\n\n'
        for graph_IO in self.graph_IO.values():
            if graph_IO.name in parameters.keys():
                code += '{}\n{{\n{}\n}}'.format(graph_IO.signature, textwrap.indent(parameters[graph_IO.name],'\t'))
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
        super().__init__('Python', '-render_layer.py', self.GLOBAL_PASS, functions, {}, graph_io)
    
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
