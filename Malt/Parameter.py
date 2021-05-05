# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

class PipelineGraph(object):
    
    def __init__(self, language, file_extension, functions, structs, graph_IO, generate_source_callback):
        self.language = language
        self.file_extension = file_extension
        self.functions = functions
        self.structs = structs
        self.graph_IO = graph_IO
        from Malt.Utils import dump_function
        self.generate_source_callback = dump_function(generate_source_callback)
    
    def generate_source(self, parameters):
        from Malt.Utils import load_function
        return load_function(self.generate_source_callback)(parameters)

class PipelineParameters(object):

    def __init__(self, scene={}, world={}, camera={}, object={}, material={}, mesh={}, light={}):
        self.scene = scene
        self.world = world
        self.camera = camera
        self.object = object
        self.material = material
        self.mesh = mesh
        self.light = light

class Type(object):
    BOOL=0
    INT=1
    FLOAT=2
    STRING=3
    #ENUM=5 #TODO
    TEXTURE=6
    GRADIENT=7
    MATERIAL=8
    #RENDER_TARGET=9 #TODO

class Parameter(object):
    def __init__(self, default_value, type, size=1, filter=None):
        self.default_value = default_value
        self.type = type
        self.size = size
        self.filter = filter

    @classmethod
    def from_uniform(cls, uniform):
        type, size = gl_type_to_malt_type(uniform.type)
        value = uniform.value
        if size > 1:
            value = tuple(value)
        else:
            value = value[0]
        #TODO: uniform length ??? (Arrays)
        return Parameter(value, type, size)
    
    @classmethod
    def from_glsl_type(cls, glsl_type):
        type, size = glsl_type_to_malt_type(glsl_type)
        value = None
        if type is Type.INT:
            value = tuple([0] * size)
        if type is Type.FLOAT:
            value = tuple([1.0] * size)
        if type is Type.BOOL:
            value = tuple([False] * size)
        return Parameter(value, type, size)

class MaterialParameter(Parameter):
    def __init__(self, default_path, extension, filter=None):
        super().__init__(default_path, Type.MATERIAL, 1, filter)
        self.extension = extension

def gl_type_to_malt_type(gl_type):
    from Malt.GL import GL
    types = {
        'FLOAT' : Type.FLOAT,
        'DOUBLE' : Type.FLOAT,
        'INT' : Type.INT,
        'BOOL' : Type.BOOL,
        'SAMPLER_1D' : Type.GRADIENT,
        'SAMPLER' : Type.TEXTURE,
    }
    sizes = {
        'VEC2' : 2,
        'VEC3' : 3,
        'VEC4' : 4,
        'MAT2' : 4,
        'MAT3' : 9,
        'MAT4' : 16,
    }
    gl_name = GL.GL_ENUMS[gl_type]

    for type_name, type in types.items():
        if type_name in gl_name:
            for size_name, size in sizes.items():
                if size_name in gl_name:
                    return (type, size)
            return (type, 1)
    
    raise Exception(gl_name, ' Uniform type not supported')

def glsl_type_to_malt_type(glsl_type):
    types = {
        'float' : Type.FLOAT,
        'vec' : Type.FLOAT,
        'mat' : Type.FLOAT,
        'double' : Type.FLOAT,
        'd' : Type.FLOAT,
        'int' : Type.INT,
        'i' : Type.INT,
        'uint' : Type.INT,
        'u' : Type.INT,
        'bool' : Type.BOOL,
        'b' : Type.BOOL,
        'sampler1D' : Type.GRADIENT,
        'sampler2D' : Type.TEXTURE,
    }
    sizes = {
        'vec2' : 2,
        'vec3' : 3,
        'vec4' : 4,
        'mat2' : 4,
        'mat3' : 9,
        'mat4' : 16,
    }
    for type_name, type in types.items():
        if glsl_type.startswith(type_name):
            for size_name, size in sizes.items():
                if size_name in glsl_type:
                    return (type, size)
            return (type, 1)
    
    return None
  