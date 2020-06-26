# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import collections

import OpenGL
OpenGL.ERROR_LOGGING = False
OpenGL.FULL_LOGGING = False
OpenGL.ERROR_ON_COPY = False
from OpenGL.GL import *

if True: 
    #For some reason PyOpenGL doesnt support the most common depth/stencil buffer by default ???
    #https://sourceforge.net/p/pyopengl/bugs/223/
    from OpenGL import images
    images.TYPE_TO_ARRAYTYPE[ GL_UNSIGNED_INT_24_8 ] = GL_UNSIGNED_INT
    images.TIGHT_PACK_FORMATS[ GL_UNSIGNED_INT_24_8 ] = 4

NULL = None
GL_ENUMS = {}
GL_NAMES = {}

if True: #create new scope to import OpenGL
    from OpenGL import GL
    for e in dir(GL):
        if e.startswith('GL_'):
            GL_ENUMS[getattr(GL, e)] = e
            GL_NAMES[e] = getattr(GL, e)

def gl_buffer(type, size, data=None):
    types = {
        GL_BYTE : GLbyte,
        GL_SHORT : GLshort,
        GL_INT : GLint,
        GL_UNSIGNED_INT : GLuint,
        GL_FLOAT : GLfloat,
        GL_DOUBLE : GLdouble,
    }
    gl_type = (types[type] * size)
    if data:
        try:
            return gl_type(*data)
        except:
            return gl_type(data)
    else:
        return gl_type()


def buffer_to_string(buffer):
    chars = []
    for char in list(buffer):
        if chr(char) == '\0':
            break
        chars.append(chr(char))
    return ''.join(chars)


def compile_gl_program(vertex, fragment):
    status = gl_buffer(GL_INT,1)
    length = gl_buffer(GL_INT,1)
    info_log = gl_buffer(GL_BYTE, 1024)    

    def compile_shader (source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        
        return shader

    vertex_shader = compile_shader(vertex, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment, GL_FRAGMENT_SHADER)

    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    
    error = None

    glGetProgramiv(program, GL_LINK_STATUS, status)
    if status[0] == GL_FALSE:
        try: #BGL
            glGetProgramInfoLog(program, 1024, length, info_log)
        except: #PYOPENGL
            info_log = glGetProgramInfoLog(program)
        error = buffer_to_string(info_log)

    return (program, error)

class GLUniform(object):
    def __init__(self, index, type, base_type, base_size, array_length, value):
        self.index = index
        self.type = type
        self.base_type = base_type
        self.base_size = base_size
        self.array_length = array_length
        self.set_function = uniform_type_set_function(self.type)
        self.value = None
        self.set_value(value)
    
    def is_sampler(self):
        return 'SAMPLER' in GL_ENUMS[self.type]
    
    def set_value(self, value):
        self.value = gl_buffer(self.base_type, self.base_size * self.array_length, value)
    
    def bind(self):
        self.set_function(self.index, self.array_length, self.value)
    
    def copy(self):
        return GLUniform(
            self.index,
            self.type, 
            self.base_type, 
            self.base_size, 
            self.array_length,
            self.value)

def uniform_type_to_base_type_and_size(type):
    base_types = {
        'GL_FLOAT' : GL_FLOAT,
        'GL_DOUBLE' : GL_DOUBLE,
        'GL_INT' : GL_INT,
        'GL_UNSIGNED_INT' : GL_UNSIGNED_INT,
        'GL_BOOL' : GL_BOOL, #TODO: check docs,
    }
    gl_sizes = {
        'VEC2' : 2,
        'VEC3' : 3,
        'VEC4' : 4,
        'MAT2' : 4,
        'MAT3' : 9,
        'MAT4' : 16,
    }
    type_name = GL_ENUMS[type]
    if 'SAMPLER' in type_name or 'IMAGE' in type_name:
        return (GL_INT, 1)
    for base_name, base_type in base_types.items():
        if type_name.startswith(base_name):
            for size_name, size in gl_sizes.items():
                if size_name in type_name:
                    return (base_type, size)
            return (base_type, 1)
    raise Exception(type_name, ' Uniform type not supported')
        
def reflect_program_uniforms(program):
    max_string_length = 128
    string_length = gl_buffer(GL_INT, 1)
    uniform_type = gl_buffer(GL_INT, 1)
    uniform_name = gl_buffer(GL_BYTE, max_string_length)
    array_length = gl_buffer(GL_INT, 1)
    uniform_count = gl_buffer(GL_INT,1)
    
    glGetProgramiv(program, GL_ACTIVE_UNIFORMS, uniform_count)

    uniforms = {}

    for i in range(0, uniform_count[0]):
        glGetActiveUniform(program, i, max_string_length, string_length,
        array_length, uniform_type, uniform_name)
        name = buffer_to_string(uniform_name)

        base_type, size = uniform_type_to_base_type_and_size(uniform_type[0])

        #TODO: Should use glGetnUniform to support arrays
        gl_get = {
            GL_FLOAT : glGetUniformfv,
            GL_DOUBLE : glGetUniformdv,
            GL_INT : glGetUniformiv,
            GL_UNSIGNED_INT : glGetUniformuiv,
            GL_BOOL : glGetUniformiv, #TODO: check,
        }
        value = gl_buffer(base_type, size * array_length[0])
        gl_get[base_type](program, i, value)

        uniforms[name] = GLUniform(i, uniform_type[0], base_type, size, array_length[0], value)
    
    return uniforms

def uniform_type_set_function(uniform_type):
    base_type, size = uniform_type_to_base_type_and_size(uniform_type)
    gl_types = {
        GL_FLOAT : 'fv',
        GL_DOUBLE : 'dv',
        GL_INT : 'iv',
        GL_UNSIGNED_INT : 'uiv',
        GL_BOOL : 'iv',
    }
    gl_size = {
        1 : '1',
        2 : '2',
        3 : '3',
        4 : '4', #TODO: Matrix2
        9 : 'Matrix3',
        16: 'Matrix4'
    }
    function_name = 'glUniform' + gl_size[size] + gl_types[base_type]
    function = globals()[function_name]
    if size > 4: #is matrix
        def set_matrix_wrapper(location, count, value):
            function(location, count, GL_FALSE, value)
        return set_matrix_wrapper
    else:
        return function 


def internal_format_to_format(internal_format):
    name = GL_ENUMS[internal_format]
    table = {
        'GL_RGBA' : GL_RGBA,
        'GL_RGB' : GL_RGB,
        'GL_RG' : GL_RG,
        'GL_R' : GL_RED,
        'GL_DEPTH_COMPONENT' : GL_DEPTH_COMPONENT,
        'GL_DEPTH24_STENCIL8' : GL_DEPTH_STENCIL,
        'GL_DEPTH32F_STENCIL8' : GL_DEPTH_STENCIL,
        'GL_STENCIL' : GL_STENCIL,
    }
    for key, value in table.items():
        if key in name:
            return value
    
    raise Exception(name, ' Texture format not supported')

def load_preprocessed_file(file_path, include_directories=[], definitions=[]):
    import pcpp
    from io import StringIO
    from os import path

    class Preprocessor(pcpp.Preprocessor):
        def on_comment(self,token):
            #Don't remove comments
            return True

    output = StringIO()
    preprocessor = Preprocessor()
    file_dir = path.dirname(file_path)
    preprocessor.add_path(file_dir)
    for directory in include_directories:
        preprocessor.add_path(directory)
    for definition in definitions:
        preprocessor.define(definition)
    preprocessor.parse(open(file_path, 'r').read())
    preprocessor.write(output)
    processed = output.getvalue()
    #fix LINE directive paths (C:\Path -> C:\\Path) to avoid compiler warnings
    processed = processed.replace('\\','\\\\')
    return processed
