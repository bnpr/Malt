# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

class PipelineGraphIO():

    def __init__(self, name, dynamic_input_types = [], dynamic_output_types = [], function=None):
        self.name = name
        self.dynamic_input_types = dynamic_input_types
        self.dynamic_output_types = dynamic_output_types
        self.function = function

class PipelineGraph():

    INTERNAL_GRAPH = 0
    GLOBAL_GRAPH = 1
    SCENE_GRAPH = 2
    
    def __init__(self, name, language, file_extension, graph_type, graph_io):
        self.name = name
        self.language = language
        self.file_extension = file_extension
        self.graph_type = graph_type
        self.libs = []
        self.lib_files = []
        self.include_paths = []
        self.functions = {}
        self.structs = {}
        self.graph_io = { io.name : io for io in graph_io } 
    
    def add_library(self, path):
        import os
        from Malt.Utils import scan_dirs
        extension = self.file_extension.split('.')[-1]
        if os.path.isdir(path):
            self.include_paths.append(path)
            def file_callback(file):
                if file.path.endswith(extension):
                    self.lib_files.append(file.path)
            scan_dirs(path, file_callback)
        else:
            self.include_paths.append(os.path.dirname(path))
            self.lib_files.append(path)
        self.libs.append(path)
    
    def setup_reflection(self):
        pass
    
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
    
    def __init__(self, name, define = None, io_wrap=None, dynamic_input_types = [], dynamic_output_types = [], shader_type=None, custom_output_start_index=0):
        super().__init__(name, dynamic_input_types, dynamic_output_types)
        self.define = define
        self.io_wrap = io_wrap
        self.shader_type = shader_type
        self.signature = None
        self.custom_output_start_index = custom_output_start_index


class GLSLPipelineGraph(PipelineGraph):

    def __init__(self, name, graph_type, default_global_scope, default_shader_src, shaders=['SHADER'], graph_io=[]):
        file_extension = f'.{name.lower()}.glsl'
        super().__init__(name, 'GLSL', file_extension, graph_type, graph_io)
        self.default_global_scope = default_global_scope
        self.default_shader_src = default_shader_src
        self.shaders = shaders
    
    def name_as_macro(self, name):
        return ''.join(c for c in name.replace(' ','_').upper() if c.isalnum() or c == '_')
    
    def get_material_define(self):
        return f'IS_{self.name_as_macro(self.name)}_SHADER'
    
    def preprocess_shader_from_source(self, source, include_paths=[], defines=[]):
        from Malt.GL.Shader import shader_preprocessor
        return shader_preprocessor(source, self.include_paths + include_paths, [self.get_material_define()] + defines)

    def setup_reflection(self):
        src = self.default_global_scope + self.default_shader_src
        for file in self.lib_files:
            src += f'\n#include "{file}"\n'
        src = self.preprocess_shader_from_source(src, [], ['VERTEX_SHADER','PIXEL_SHADER','REFLECTION'])
        from Malt.GL.Shader import glsl_reflection
        reflection = glsl_reflection(src, self.include_paths)
        functions = reflection["functions"]
        structs = reflection["structs"]
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
        self.functions = functions
        self.structs = structs
    
    def generate_source(self, parameters):
        import textwrap
        from Malt.SourceTranspiler import GLSLTranspiler
        code = ''
        for graph_io in self.graph_io.values():
            if graph_io.name in parameters.keys() and graph_io.define:
                code += '#define {}\n'.format(graph_io.define)
        code += '\n\n' + self.default_global_scope + '\n\n'
        for file in self.lib_files:
            code += f'#include "{file}"\n'
        code += '\n\n' + parameters['GLOBAL'] + '\n\n'
        for graph_io in self.graph_io.values():
            if graph_io.name in parameters.keys():
                code += GLSLTranspiler.preprocessor_wrap(graph_io.shader_type,
                '{}\n{{\n{}\n}}'.format(graph_io.signature, textwrap.indent(parameters[graph_io.name],'\t')))
        code += '\n\n'
        return code
    
    def compile_material(self, source, include_paths=[]):
        from Malt.GL.Shader import Shader
        shaders = {}
        for shader in self.shaders:
            vertex_src = self.preprocess_shader_from_source(source, include_paths, [shader, 'VERTEX_SHADER'])
            pixel_src = self.preprocess_shader_from_source(source, include_paths, [shader, 'PIXEL_SHADER'])
            shaders[shader] = Shader(vertex_src, pixel_src)
        return shaders

class PythonGraphIO(PipelineGraphIO):

    COMMON_IO_TYPES = ['Texture']

    def __init__(self, name, dynamic_input_types = [], dynamic_output_types = [], function=None):
        super().__init__(name, dynamic_input_types, dynamic_output_types, function)

class PythonPipelineGraph(PipelineGraph):
    
    def __init__(self, name, graph_io):
        extension = f'-{name}.py'
        super().__init__(name, 'Python', extension, self.GLOBAL_GRAPH, graph_io)
        self.node_instances = {}
        self.nodes = {}

    def get_serializable_copy(self):
        result = super().get_serializable_copy()
        result.nodes = None
        result.node_instances = None
        return result
    
    def setup_reflection(self):
        import importlib.util
        nodes = []
        for file in self.lib_files:
            try:
                spec = importlib.util.spec_from_file_location("_dynamic_node_module_", file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                nodes.append(module.NODE)
            except:
                import traceback
                traceback.print_exc()
                print('filepath : ', file)
        self.functions = {}
        self.structs = {}
        for node_class in nodes:
            reflection = node_class.reflect()
            self.functions[reflection['name']] = reflection
            self.nodes[reflection['name']] = node_class
    
    def generate_source(self, parameters):
        src = ''
        for io in self.graph_io.keys():
            if io in parameters.keys():
                src += parameters[io]
        return src
    
    def run_source(self, pipeline, source, PARAMETERS, IN, OUT):
        try:
            def run_node(node_name, node_type, parameters):
                if node_name not in self.node_instances.keys():
                    node_class = self.nodes[node_type]
                    self.node_instances[node_name] = node_class(pipeline)
                parameters['__GLOBALS__'] = PARAMETERS
                self.node_instances[node_name].execute(parameters)
            exec(source)
        except:
            import traceback
            traceback.print_exc()
            print('SOURCE:\n', source)
            print('PARAMETERS: ', PARAMETERS)
            print('IN: ', IN)
            print('OUT: ', OUT)
