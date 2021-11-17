# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import ctypes, os

from Malt.GL.GL import *
from Malt.Utils import LOG


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
                LOG.debug("Texture Uniform {} not found".format(name))
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
        glBindBufferRange(GL_UNIFORM_BUFFER, uniform_block['bind'], self.buffer[0], 0, min(self.size, uniform_block['size']))
    
    def __del__(self):
        try:
            glDeleteBuffers(1, self.buffer[0])
        except:
            #TODO: Make sure GL objects are deleted in the correct context
            pass


def shader_preprocessor(shader_source, include_directories=[], definitions=[]):
    import tempfile, subprocess, sys, platform
    
    shader_source = shader_source + '\n'
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(shader_source.encode('utf-8'))
    tmp.close()

    py_version = str(sys.version_info[0])+str(sys.version_info[1])
    dependencies_path = os.path.join(os.path.dirname(__file__), '..', f'.Dependencies-{py_version}')
    mcpp = os.path.join(dependencies_path, f'mcpp-{platform.system()}')

    args = [mcpp]
    for directory in include_directories:
        args.append('-I'+directory)
    for definition in definitions:
        args.append('-D'+definition)
    args.append(tmp.name)

    try:
        result = subprocess.run(args, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
    except PermissionError:
        import stat
        os.chmod(mcpp, os.stat(mcpp).st_mode | stat.S_IEXEC)
        result = subprocess.run(args, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
    finally:
        os.remove(tmp.name)
        if result.returncode != 0:
            raise Exception(result.stderr.decode('utf-8'))
        else:
            return result.stdout.decode('utf-8')


__LINE_DIRECTIVE_SUPPORT = None

def directive_line_support():
    global __LINE_DIRECTIVE_SUPPORT
    if __LINE_DIRECTIVE_SUPPORT is not None:
        return __LINE_DIRECTIVE_SUPPORT
    def try_compilation (line_directive):
        src = f'''
        #version 410 core
        #extension GL_ARB_shading_language_include : enable
        {line_directive}
        layout (location = 0) out vec4 OUT_COLOR;
        void main() {{ OUT_COLOR = vec4(1); }}
        '''
        status = gl_buffer(GL_INT,1)
        shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(shader, src)
        glCompileShader(shader)
        glGetShaderiv(shader, GL_COMPILE_STATUS, status)
        glDeleteShader(shader)
        return status[0] != GL_FALSE
    
    if try_compilation('#line 1 "/ .A1a1!·$%&/()=?¿|@#~€/test.glsl"'):
        __LINE_DIRECTIVE_SUPPORT = 'FULL'
    elif try_compilation('#line 1 "/Basic test/test_1.glsl"'):
        __LINE_DIRECTIVE_SUPPORT = 'BASIC_STRING'
    elif try_compilation('#line 1 1'):
        __LINE_DIRECTIVE_SUPPORT = 'FILE_NUMBER'
    elif try_compilation('#line 1'):
        __LINE_DIRECTIVE_SUPPORT = 'LINE_NUMBER'
    else:
        __LINE_DIRECTIVE_SUPPORT = 'NONE'
    
    return __LINE_DIRECTIVE_SUPPORT


def fix_line_directive_paths(source):
    support = directive_line_support()
    if support == 'FULL':
        return source
    include_paths = []
    result = ''
    for line in source.splitlines(keepends=True):
        if line.startswith("#line") and '"' in line:
            start = line.index('"')
            end = line.index('"', start + 1)
            include_path = line[start:end+1]
            if support == 'BASIC_STRING':
                basic_string = ''.join([c for c in include_path if c.isalnum() or c in '/._ '])
                line = line.replace(include_path, f'"{basic_string}"')
            elif support == 'FILE_NUMBER':
                    if include_path not in include_paths:
                        include_paths.append(include_path)
                    line = line.replace(include_path, str(include_paths.index(include_path)))
            elif support == 'LINE_NUMBER':
                if '"' in line:
                    line = line.split('"',1)[0]
            else:
                line = "\n"
        result += line    
    return result


def compile_gl_program(vertex, fragment):
    status = gl_buffer(GL_INT,1)
    info_log = gl_buffer(GL_BYTE, 1024)

    error = ""

    def compile_shader (source, shader_type):
        bindless_setup = ''
        if hasGLExtension('GL_ARB_bindless_texture'):
            bindless_setup = '''
            #extension GL_ARB_bindless_texture : enable
            layout(bindless_sampler) uniform;
            '''
        import textwrap
        source = textwrap.dedent(f'''
        #version 410 core
        #extension GL_ARB_shading_language_include : enable
        {bindless_setup}
        #line 1 "src"
        ''') + source
        source = fix_line_directive_paths(source)
        
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        glGetShaderiv(shader, GL_COMPILE_STATUS, status)
        if status[0] == GL_FALSE:
            info_log = glGetShaderInfoLog(shader)
            nonlocal error
            error += 'SHADER COMPILER ERROR :\n' + buffer_to_string(info_log)
        
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

def glsl_reflection(code, root_path = None):
    import tempfile, subprocess, json
    GLSLParser = os.path.join(os.path.dirname(__file__), 'GLSLParser', '.bin', 'GLSLParser')
    root_path = os.path.normpath(root_path)
    
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(code.encode('utf-8'))
    tmp.close()
    
    try:
        json_string = subprocess.check_output([GLSLParser, tmp.name])
    except PermissionError:
        import stat
        os.chmod(GLSLParser, os.stat(GLSLParser).st_mode | stat.S_IEXEC)
        json_string = subprocess.check_output([GLSLParser, tmp.name])
    
    os.remove(tmp.name)
    
    reflection = json.loads(json_string)

    def fix_paths(dic):
        for e in dic.values():
            path = e["file"]
            path = os.path.normpath(path)
            try: path = os.path.relpath(path, root_path)
            except: pass
            e["file"] = path
    
    fix_paths(reflection["structs"])
    fix_paths(reflection["functions"])

    return reflection


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

