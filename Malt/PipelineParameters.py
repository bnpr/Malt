class PipelineParameters():

    def __init__(self, scene={}, world={}, camera={}, object={}, material={}, mesh={}, light={}):
        self.scene = scene
        self.world = world
        self.camera = camera
        self.object = object
        self.material = material
        self.mesh = mesh
        self.light = light

class Type():
    BOOL=0
    INT=1
    FLOAT=2
    STRING=3
    ENUM=4
    OTHER=5
    TEXTURE=6
    GRADIENT=7
    MATERIAL=8
    #RENDER_TARGET=9 #TODO
    GRAPH=10

    @classmethod
    def string_list(cls):
        return ['Bool', 'Int', 'Float', 'String', 'Other', 'Enum', 'Texture', 'Gradient',
            'Material', 'RenderTarget', 'Graph']
    @classmethod
    def to_string(cls, type):
        return cls.string_list()[type]
    @classmethod
    def from_string(cls, type):
        return cls.string_list().index(type)

class Parameter():
    def __init__(self, default_value, type, size=1, filter=None, subtype=None, doc=None):
        self.default_value = default_value
        self.type = type
        self.subtype = subtype
        self.size = size
        self.filter = filter
        self.doc = doc
    
    def type_string(self):
        if self.type == Type.OTHER:
            return self.default_value
        else:
            return Type.to_string(self.type)

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
    def from_glsl_type(cls, glsl_type, subtype=None, default_value=None):
        type, size = glsl_type_to_malt_type(glsl_type)
        if subtype and subtype.startswith('ENUM'):
            try:
                enum_options = subtype.split('ENUM(')[1][:-1]
                enum_options = enum_options.split(',')
                if isinstance(default_value, int):
                    default_value = enum_options[default_value]
                if default_value is None:
                    default_value = enum_options[0]
                return EnumParameter(enum_options, default_value)
            except:
                pass
        if default_value is None:
            if type is Type.INT:
                default_value = tuple([0] * size)
            if type is Type.FLOAT:
                default_value = tuple([0.0] * size)
            if type is Type.BOOL:
                default_value = tuple([False] * size)
            if default_value and len(default_value) == 1:
                default_value = default_value[0]
            overrides = {
                ('vec3',None):(0.5,0.5,0.5),
                ('vec4',None):(0.5,0.5,0.5,1.0),
                ('vec3','Color'):(0.5,0.5,0.5),
                ('vec4','Color'):(0.5,0.5,0.5,1.0),
                ('vec3','Normal'):(1.0,0.0,0.0),
                ('vec4','Quaternion'):(0.0,0.0,0.0,1.0),
                ('mat3',None):(
                    1.0,0.0,0.0,
                    0.0,1.0,0.0,
                    0.0,0.0,1.0,
                ),
                ('mat4',None):(
                    1.0,0.0,0.0,0.0,
                    0.0,1.0,0.0,0.0,
                    0.0,0.0,1.0,0.0,
                    0.0,0.0,0.0,1.0,
                ),
            }
            override = overrides.get((glsl_type, subtype))
            if override is not None:
                default_value = override
        return Parameter(default_value, type, size, subtype=subtype)

class MaterialParameter(Parameter):
    def __init__(self, default_path, extension, graph_type=None, filter=None, doc=None):
        super().__init__(default_path, Type.MATERIAL, 1, filter, extension, doc)
        self.extension = extension
        self.graph_type = graph_type

class GraphParameter(Parameter):
    def __init__(self, default_path, graph_type, filter=None, doc=None):
        super().__init__(default_path, Type.GRAPH, 1, filter, graph_type, doc)
        self.graph_type = graph_type

class EnumParameter(Parameter):
    def __init__(self, options, default_option, filter=None, doc=None):
        self.enum_options = options
        super().__init__(default_option, Type.ENUM, 1, filter, None, doc)
    
    def from_index(self, index):
        return self.enum_options[index]

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
