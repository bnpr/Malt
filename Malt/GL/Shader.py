# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import ctypes, os

from Malt.GL.GL import *
from Malt.Utils import log


class Shader(object):

    def __init__(self, vertex_source, pixel_source):
        if vertex_source and pixel_source:
            self.vertex_source = vertex_source
            self.pixel_source = pixel_source
            self.program, self.error = compile_gl_program(vertex_source, pixel_source)
            self.validator = glslang_validator(vertex_source,'vert')
            self.validator += glslang_validator(pixel_source,'frag')
            if self.validator == '':
                self.validator = None
        else:
            self.vertex_source = vertex_source
            self.pixel_source = pixel_source
            self.program = None
            self.error = 'NO SOURCE'
            self.validator = None
        self.uniforms = {}
        self.textures = {}
        self.uniform_blocks = {}
        if self.error == '':
            self.error = None
            self.uniforms = reflect_program_uniforms(self.program)
            texture_index = 0
            for name, uniform in self.uniforms.items():
                if uniform.is_sampler():
                    uniform.set_value(texture_index)
                    texture_index += 1 
                    self.textures[name] = None

            self.uniform_blocks = reflect_program_uniform_blocks(self.program)
        
    def bind(self):
        glUseProgram(self.program)
        for uniform in self.uniforms.values():
            uniform.bind()
        for name, texture in self.textures.items():
            if name not in self.uniforms:
                log('DEBUG', "Texture Uniform {} not found".format(name))
                continue
            glActiveTexture(GL_TEXTURE0 + self.uniforms[name].value[0])
            if texture:
                if hasattr(texture, 'bind'):
                    texture.bind()
                else: #Then it's just a externally generated bind code
                    glBindTexture(GL_TEXTURE_2D, texture)
            else:
                glBindTexture(GL_TEXTURE_2D, 0)
    
    def copy(self):
        new = Shader(None, None)
        new.vertex_source = self.vertex_source
        new.pixel_source = self.pixel_source
        new.program = self.program
        new.error = self.error
        for name, uniform in self.uniforms.items():
            new.uniforms[name] = uniform.copy()
        for name, texture in self.textures.items():
            new.textures[name] = texture
        for name, block in self.uniform_blocks.items():
            new.uniform_blocks[name] = block
        
        return new
    
    def __del__(self):
        #TODO: Programs are shared between Shaders. Should refcount them
        pass


class GLUniform(object):
    def __init__(self, index, type, value, array_length=1):
        self.index = index
        self.type = type
        self.base_type, self.base_size = uniform_type_to_base_type_and_size(self.type)
        self.array_length = array_length
        self.set_function = uniform_type_set_function(self.type)
        self.value = None
        self.set_value(value)
    
    def is_sampler(self):
        return 'SAMPLER' in GL_ENUMS[self.type]
    
    def set_value(self, value):
        if self.base_type == GL_UNSIGNED_INT:
            try: value = max(0, value)
            except: value = [max(0, v) for v in value]
        self.value = gl_buffer(self.base_type, self.base_size * self.array_length, value)
    
    def set_buffer(self, buffer):
        self.value = buffer
    
    def bind(self, buffer=None):
        if buffer is None:
            buffer = self.value
        self.set_function(self.index, self.array_length, buffer)
    
    def copy(self):
        return GLUniform(
            self.index,
            self.type, 
            self.value, 
            self.array_length)


class UBO(object):

    def __init__(self):
        self.size = 0
        self.buffer = gl_buffer(GL_INT, 1)
        glGenBuffers(1, self.buffer)
    
    def load_data(self, structure):
        self.size = ctypes.sizeof(structure)
        glBindBuffer(GL_UNIFORM_BUFFER, self.buffer[0])
        glBufferData(GL_UNIFORM_BUFFER, self.size, ctypes.pointer(structure), GL_STREAM_DRAW)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def bind(self, uniform_block):
        if self.size != uniform_block['size']:
            log('DEBUG', "non-matching size UBO bindind")
            log('DEBUG', "name : {} | bind : {} | UBO size : {} | uniform block size : {}".format(
                uniform_block['name'], uniform_block['bind'], self.size, uniform_block['size']
            ))

        glBindBufferRange(GL_UNIFORM_BUFFER, uniform_block['bind'], self.buffer[0], 0, self.size)
    
    def __del__(self):
        try:
            glDeleteBuffers(1, self.buffer[0])
        except:
            #TODO: Make sure GL objects are deleted in the correct context
            pass


def shader_preprocessor(shader_source, include_directories=[], definitions=[]):
    import pcpp
    from io import StringIO
    from os import path

    class Preprocessor(pcpp.Preprocessor):
        def on_comment(self,token):
            #Don't remove comments
            return True

    output = StringIO()
    preprocessor = pcpp.Preprocessor()
    preprocessor.path = []
    for directory in include_directories:
        preprocessor.add_path(directory)
    preprocessor.rewrite_paths = []
    for definition in definitions:
        preprocessor.define(definition)
    preprocessor.parse(shader_source)
    preprocessor.write(output)
    processed = output.getvalue()
    #fix LINE directive paths (C:\Path -> C:/Path) to avoid compiler errors/warnings
    processed = processed.replace('\\','/')
    
    def remove_line_directive_paths(source):
        #Paths in line directives are not supported in some drivers, so we replace paths with numbers
        include_paths = []
        result = ''
        for line in source.splitlines(keepends=True):
            if line.startswith("#line"):
                continue
                if '"' in line:
                    start = line.index('"')
                    end = line.index('"', start + 1)
                    include_path = line[start:end+1]
                    if include_path not in include_paths:
                        include_paths.append(include_path)
                    line = line.replace(include_path, str(include_paths.index(include_path)))
                    line = line.replace('\n', ' //{}\n'.format(include_path))
            result += line    
        return result
    
    if True:#hasGLExtension('GL_ARB_shading_language_include') == False:
        processed = remove_line_directive_paths(processed)

    return processed


def compile_gl_program(vertex, fragment):
    status = gl_buffer(GL_INT,1)
    error = ""

    def compile_shader (source, shader_type):
        shader = glCreateShader(shader_type)

        source_ascii = source.encode('ascii')

        import ctypes
        c_shader = GLuint(shader)
        c_count = GLsizei(1)
        c_source = (ctypes.c_char_p * 1)(source_ascii)
        c_length = (GLint * 1)(len(source_ascii))

        glShaderSource.wrappedOperation(c_shader, c_count, c_source, c_length)
        
        glCompileShader(shader)

        glGetShaderiv(shader, GL_COMPILE_STATUS, status)
        if status[0] == GL_FALSE:
            info_log = glGetShaderInfoLog(shader)
            nonlocal error
            error += 'SHADER COMPILER ERROR :\n' + buffer_to_string(info_log)
            import logging
            logging.error("SHADER ERROR -------------------")
            logging.error(buffer_to_string(info_log))
            logging.error("SHADER SOURCE -------------------")
            logging.error(source_ascii)

        
        return shader

    vertex_shader = compile_shader(vertex, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment, GL_FRAGMENT_SHADER)

    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    
    glGetProgramiv(program, GL_LINK_STATUS, status)
    if status[0] == GL_FALSE:
        info_log = glGetProgramInfoLog(program)
        error += 'SHADER LINKER ERROR :\n' + buffer_to_string(info_log)

    return (program, error)


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

        #Uniform location can be different from index
        location = glGetUniformLocation(program, name)

        if location == -1:
            continue #A built-in uniform or an Uniform Block

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
        gl_get[base_type](program, location, value)

        if array_length[0] > 1:
            for i in range(array_length[0]):
                _name = '[{}]'.format(i).join(name.rsplit('[0]', 1))
                _value = value[i*size:i*size+size]
                _location = glGetUniformLocation(program, _name)
                uniforms[_name] = GLUniform(_location, uniform_type[0], _value)
        else:
            uniforms[name] = GLUniform(location, uniform_type[0], value)
    
    return uniforms


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


def reflect_program_uniform_blocks(program):
    block_count = gl_buffer(GL_INT,1)
    max_string_length = 128
    block_name = gl_buffer(GL_BYTE, max_string_length)
    block_bind = gl_buffer(GL_INT, 1)
    block_size = gl_buffer(GL_INT, 1)

    glGetProgramiv(program, GL_ACTIVE_UNIFORM_BLOCKS, block_count)

    blocks = {}
    for i in range(0, block_count[0]):
        glGetActiveUniformBlockName(program, i, max_string_length, NULL, block_name)
        name = buffer_to_string(block_name)
        glUniformBlockBinding(program, i, i) # All Uniform Blocks are binded at 0 by default. :/
        glGetActiveUniformBlockiv(program, i, GL_UNIFORM_BLOCK_BINDING, block_bind)
        glGetActiveUniformBlockiv(program, i, GL_UNIFORM_BLOCK_DATA_SIZE, block_size)
        blocks[name] = {
            'bind' : block_bind[0],
            'size' : block_size[0],
            'name' : name,
        }
    
    return blocks

USE_GLSLANG_VALIDATOR = False

import pyparsing

class GLSL_Reflection(object):
    # Based on github.com/rougier/glsl-parser.
    # Copyright (c) 2014, Nicolas P. Rougier. (new) BSD License.
    LPAREN = pyparsing.Literal("(").suppress()
    RPAREN = pyparsing.Literal(")").suppress()
    LBRACE = pyparsing.Literal("{").suppress()
    RBRACE = pyparsing.Literal("}").suppress()
    LBRACKET = pyparsing.Literal("[").suppress()
    RBRACKET = pyparsing.Literal("]").suppress()
    END = pyparsing.Literal(";").suppress()
    STRUCT = pyparsing.Literal("struct").suppress()
    IDENTIFIER = pyparsing.Word(pyparsing.alphas + '_', pyparsing.alphanums + '_')
    TYPE = pyparsing.Word(pyparsing.alphas + '_', pyparsing.alphanums + "_")
    INT = pyparsing.Word(pyparsing.nums)
    PRECISION = pyparsing.Regex('lowp |mediump |high ')
    IO = pyparsing.Regex('in |out |inout ')

    ARRAY_SIZE = LBRACKET + INT("array_size") + RBRACKET

    MEMBER = pyparsing.Group(
        pyparsing.Optional(PRECISION)("precision") +
        TYPE("type") +
        IDENTIFIER("name") +
        pyparsing.Optional(ARRAY_SIZE)
    )

    MEMBERS = pyparsing.delimitedList(MEMBER, ";")("member*") + END

    STRUCT_DEF = (
        STRUCT + IDENTIFIER("name") + 
        LBRACE + pyparsing.Optional(MEMBERS)("members") + RBRACE
    )

    STRUCT_DEF.ignore(pyparsing.cStyleComment)
    STRUCT_DEF.ignore(pyparsing.dblSlashComment)
    STRUCT_DEF.parseWithTabs() #Otherwise star-end indices don't match

    @classmethod
    def get_file_path(cls, code, position, root_path = None):
        line_directive_start = code.rfind('#line', 0, position)
        if line_directive_start == -1:
            return ''
        path_start = code.find('"', line_directive_start)
        if path_start == -1:
            return ''
        path_start+=1
        path_end = code.find('"', path_start)
        if path_end == -1:
            return ''
        path = code[path_start:path_end]
        root_path = os.path.normpath(root_path)
        path = os.path.normpath(path)
        try:
            return os.path.relpath(path, root_path)
        except:
            return path
    
    @classmethod
    def reflect_structs(cls, code, root_path = None):
        structs = {}
        for struct, start, end in cls.STRUCT_DEF.scanString(code):
            dictionary = {
                'name' : struct.name,
                'file' : cls.get_file_path(code, start, root_path),
                'members' : []
            }
            for member in struct.members:
                dictionary['members'].append({
                    'name' : member.name,
                    'type' : member.type,
                    'size' : int(member.array_size) if member.array_size else 0
                })
            structs[struct.name] = dictionary
        return structs

    PARAMETER = pyparsing.Group(
        pyparsing.Optional(IO)("io") +
        pyparsing.Optional(PRECISION)("precision") +
        TYPE("type") + pyparsing.Optional(IDENTIFIER)("name") +
        pyparsing.Optional(ARRAY_SIZE)
    )

    PARAMETERS = pyparsing.delimitedList(PARAMETER)("parameter*")

    FUNCTION = (
        pyparsing.Optional(PRECISION)("precision") +
        TYPE("type") + IDENTIFIER("name") +
        LPAREN + pyparsing.Optional(PARAMETERS)("parameters") + RPAREN +
        pyparsing.originalTextFor(pyparsing.nestedExpr("{", "}"))("code")
    )

    FUNCTION.ignore(pyparsing.cStyleComment)
    FUNCTION.ignore(pyparsing.dblSlashComment)
    FUNCTION.parseWithTabs() #Otherwise star-end indices don't match

    @classmethod
    def reflect_functions(cls, code, root_path = None):
        functions = {}
        for function, start, end in cls.FUNCTION.scanString(code):
            dictionary = {
                'name' : function.name,
                'type' : function.type,
                'file' : cls.get_file_path(code, start, root_path),
                'parameters' : []
            }
            for parameter in function.parameters:
                dictionary['parameters'].append({
                    'name' : parameter.name,
                    'type' : parameter.type,
                    'size' : int(parameter.array_size) if parameter.array_size else 0,
                    'io' : parameter.io.replace(' ',''),#TODO
                })
            functions[function.name] = dictionary
        return functions


def glslang_validator(source, stage):
    if not USE_GLSLANG_VALIDATOR:
        return ''
        
    import subprocess
    import tempfile
    import os
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(source.replace('GL_ARB_shading_language_include', 'GL_GOOGLE_include_directive').encode('utf-8'))
    tmp.close()
    out = None
    try:
        out = subprocess.check_output(['glslangValidator','-S',stage,tmp.name])
        if out != b'':
            out = out
    except subprocess.CalledProcessError as error:
        out = error.output
    except:
        pass
    os.unlink(tmp.name)
    if out:
        out = out.decode('utf-8')
        #Remove the first line since it's the path to a temp file
        out = out.split('\n')[1]
        stages = {
            'vert' : 'VERTEX',
            'frag' : 'PIXEL',
        }
        return '{} SHADER VALIDATION :\n{}'.format(stages[stage], out)
    else:
        return ''

