class PipelineGraphIO():

    def __init__(self, name, dynamic_input_types = [], dynamic_output_types = []):
        self.name = name
        self.signature = None
        self.function = None
        self.dynamic_input_types = dynamic_input_types
        self.dynamic_output_types = dynamic_output_types

class PipelineGraph():

    INTERNAL_GRAPH = 0
    GLOBAL_GRAPH = 1
    SCENE_GRAPH = 2
    
    def __init__(self, name, language, file_extension, graph_type, graph_io):
        self.name = name
        self.language = language
        self.file_extension = file_extension
        self.graph_type = graph_type
        self.functions = None
        self.structs = None
        self.graph_io = { io.name : io for io in graph_io } 
    
    def setup_reflection(self, functions, structs):
        self.functions = functions
        self.structs = structs
        for io in self.graph_io.values():
            io.function = functions[io.name]
            io.signature = io.function['signature']
        for key in [*functions.keys()]:
            name = functions[key]['name']
            if name.startswith('_') or name.isupper() or name == 'main':
                functions.pop(key)
        for name in [*structs.keys()]:
            if name.startswith('_'): #TODO: Upper???
                structs.pop(name)
    
    def generate_source(self, parameters):
        return ''
    
    def get_serializable_copy(self):
        from copy import copy
        return copy(self)


class GLSLGraphIO(PipelineGraphIO): 

    COMMON_INPUT_TYPES = ['sampler2D', 'usampler2D', 'isampler2D']
    COMMON_OUTPUT_TYPES = [
        'float','vec2','vec3','vec4',
        'uint','uvec2','uvec3','uvec4',
        'int','ivec2','ivec3','ivec4',
    ]
    
    def __init__(self, name, define = None, dynamic_input_types = [], dynamic_output_types = [], shader_type=None, custom_output_start_index=0):
        super().__init__(name, dynamic_input_types, dynamic_output_types)
        self.define = define
        self.shader_type = shader_type
        self.custom_output_start_index = custom_output_start_index


class GLSLPipelineGraph(PipelineGraph):

    def __init__(self, name, graph_type, default_global_scope, shaders=['SHADER'], graph_io=[]):
        file_extension = f'.{name.lower()}.glsl'
        super().__init__(name, 'GLSL', file_extension, graph_type)
        self.default_global_scope = default_global_scope
        self.shaders = shaders
        self.graph_io = graph_io
    
    def name_as_macro(self, name):
        return ''.join(c for c in name.replace('','_').upper() if c.is_alnum() or c == '_')
    
    def get_material_define(self):
        return f'IS_{self.name_as_macro(self.name)}_SHADER'

    def setup_reflection(self, pipeline, source):
        source = self.default_global_scope + source
        source = pipeline.preprocess_shader_from_source(source, [], [self.get_material_define(), 'VERTEX_SHADER','PIXEL_SHADER','REFLECTION'])
        root_path = pipeline.SHADER_INCLUDE_PATHS #TODO: pass a list
        from . GL.Shader import glsl_reflection
        reflection = glsl_reflection(source, root_path)
        super().setup_reflection(reflection["functions"], reflection["structs"])
    
    def generate_source(self, parameters):
        import textwrap
        code = ''
        for graph_IO in self.graph_IO.values():
            if graph_IO.name in parameters.keys() and graph_IO.define:
                code += '#define {}\n'.format(graph_IO.define)
        code += '\n\n' + self.default_global_scope + '\n\n' + parameters['GLOBAL'] + '\n\n'
        for graph_IO in self.graph_IO.values():
            if graph_IO.name in parameters.keys():
                if graph_IO.shader_type:
                    code += f'#ifdef {graph_IO.shader_type}\n'
                code += '{}\n{{\n{}\n}}'.format(graph_IO.signature, textwrap.indent(parameters[graph_IO.name],'\t'))
                if graph_IO.shader_type:
                    code += f'\n#endif //{graph_IO.shader_type}\n'
        code += '\n\n'
        return code
    
    def compile_material(self, pipeline, source, include_paths=[], custom_passes=[]):
        shaders = {}
        for shader in self.shaders:
            shaders[shader] = [self.get_material_define(), shader]
            for custom_pass in custom_passes:
                shaders[f'{custom_pass}'] = [self.get_material_define(), shader, self.name_as_macro(custom_pass)]
        return pipeline.compile_shaders_from_source(source, include_paths, shaders)

class PythonPipelineGraph(PipelineGraph):
    
    def __init__(self, name, function_nodes, graph_io_reflection):
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
        extension = f'-{name}.py'
        super().__init__(name, 'Python', extension, self.GLOBAL_GRAPH, functions, {}, graph_io)
        self.setup_reflection(functions, None)
    
    def generate_source(self, parameters):
        src = ''
        for io in self.graph_IO.keys():
            if io in parameters.keys():
                src += parameters[io]
        return src
    
    def run_source(self, pipeline, source, PARAMETERS, IN, OUT):
        try:
            def run_node(node_name, node_type, parameters):
                if node_name not in self.node_instances.keys():
                    node_class = self.nodes[node_type]
                    self.node_instances[node_name] = node_class(pipeline)
                self.node_instances[node_name].execute(parameters)
            exec(source)
        except:
            import traceback
            traceback.print_exc()
            print('SOURCE:\n', source)
            print('PARAMETERS: ', PARAMETERS)
            print('IN: ', IN)
            print('OUT: ', OUT)
