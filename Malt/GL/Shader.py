import ctypes, os

from Malt.GL.GL import *
from Malt.Utils import LOG


class Shader():

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
            uniform = self.uniforms[name]
            glActiveTexture(GL_TEXTURE0 + uniform.value[0])
            if texture:
                if hasattr(texture, 'bind'):
                    texture.bind()
                else: #Then it's just a externally generated bind code
                    glBindTexture(uniform.texture_type(), texture)
            else:
                glBindTexture(uniform.texture_type(), 0)
    
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


class GLUniform():
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
    
    def texture_type(self):
        if self.is_sampler() == False:
            return None
        table = {
            '1D_ARRAY': GL_TEXTURE_1D_ARRAY,
            '_1D': GL_TEXTURE_1D,
            '2D_ARRAY': GL_TEXTURE_2D_ARRAY,
            '_2D': GL_TEXTURE_2D,
            '_3D': GL_TEXTURE_3D,
            'CUBE_MAP_ARRAY': GL_TEXTURE_CUBE_MAP_ARRAY,
            '_CUBE_MAP': GL_TEXTURE_CUBE_MAP,
        }
        name = GL_ENUMS[self.type]
        for key, value in table.items():
            if key in name:
                return value
    
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


class UBO():

    BINDS = {}

    def __init__(self):
        self.size = 0
        self.buffer = gl_buffer(GL_INT, 1)
        self.location = None
        glGenBuffers(1, self.buffer)
    
    def load_data(self, structure):
        self.size = ctypes.sizeof(structure)
        glBindBuffer(GL_UNIFORM_BUFFER, self.buffer[0])
        glBufferData(GL_UNIFORM_BUFFER, self.size, ctypes.pointer(structure), GL_STREAM_DRAW)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def bind(self, uniform_block):
        location = uniform_block['bind']
        if self.location != location or self.BINDS[location] != self:
            glBindBufferRange(GL_UNIFORM_BUFFER, location, self.buffer[0], 0, min(self.size, uniform_block['size']))
            self.location = location
            self.BINDS[location] = self
    
    def __del__(self):
        glDeleteBuffers(1, self.buffer[0])


def shader_preprocessor(shader_source, include_directories=[], definitions=[]):
    import tempfile, subprocess, sys, platform
    
    shader_source = shader_source + '\n'
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(shader_source.encode('utf-8'))
    tmp.close()

    py_version = str(sys.version_info[0])+str(sys.version_info[1])
    dependencies_path = os.path.join(os.path.dirname(__file__), '..', f'.Dependencies-{py_version}')
    mcpp = os.path.join(dependencies_path, f'mcpp-{platform.system()}')

    command = f'"{mcpp}"'
    command += ' -C' #keep comments
    for directory in include_directories:
        command += f' -I"{directory}"'
    for definition in definitions:
        command += f' -D"{definition}"'
    command += f' "{tmp.name}"'
    
    if platform.system() == 'Windows':
        #run with utf8 code page to support non-ascii paths
        command = f'CHCP 65001 > nul && {command}'
    
    try:
        result = subprocess.run(command, shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception(result.stderr.decode('utf-8'))
    except:
        import stat
        os.chmod(mcpp, os.stat(mcpp).st_mode | stat.S_IEXEC)
        result = subprocess.run(command, shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
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

    hash_src = vertex + fragment
    ''.splitlines()
    hash_src = ''.join([line for line in hash_src.splitlines(True) if line.startswith('#line') == False])
    import hashlib, tempfile
    shader_hash = hashlib.sha1(hash_src.encode()).hexdigest()
    cache_folder = os.path.join(tempfile.gettempdir(), 'MALT_SHADERS_CACHE')
    os.makedirs(cache_folder, exist_ok=True)
    cache_path = os.path.join(cache_folder, shader_hash+'.bin')
    format_path = os.path.join(cache_folder, shader_hash+'.fmt')
    cache, format = None, None
    if os.path.exists(cache_path) and os.path.exists(format_path):
        from pathlib import Path
        Path(cache_path).touch()
        with open(cache_path, 'rb') as f:
            bin = f.read()
            cache = (GLubyte*len(bin)).from_buffer_copy(bin)
        Path(format_path).touch()
        with open(format_path, 'rb') as f:
            format = GLuint.from_buffer_copy(f.read())
    
    program = glCreateProgram()
    error = ""

    if cache:
        glProgramBinary(program, format, cache, len(cache))
        glGetProgramiv(program, GL_LINK_STATUS, status)
        if status[0] != GL_FALSE:
            return (program, error)

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

    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    
    glGetProgramiv(program, GL_LINK_STATUS, status)
    if status[0] == GL_FALSE:
        info_log = glGetProgramInfoLog(program)
        error += 'SHADER LINKER ERROR :\n' + buffer_to_string(info_log)
    else:
        length = gl_buffer(GL_INT, 1)
        glGetProgramiv(program, GL_PROGRAM_BINARY_LENGTH, length)
        format = gl_buffer(GL_UNSIGNED_INT, 1)
        buffer = gl_buffer(GL_UNSIGNED_BYTE, length[0])
        glGetProgramBinary(program, length[0], NULL, format, buffer)
        with open(cache_path, 'wb') as f:
            f.write(buffer)
        with open(format_path, 'wb') as f:
            f.write(format)

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

    query_indices = gl_buffer(GL_INT, uniform_count[0])
    for i in range(len(query_indices)):
        query_indices[i] = i
    block_indices = gl_buffer(GL_INT, uniform_count[0])
    glGetActiveUniformsiv(program, uniform_count[0], query_indices, GL_UNIFORM_BLOCK_INDEX, block_indices)

    for i in range(0, uniform_count[0]):
        if block_indices[i] != -1:
            continue #A built-in uniform or an Uniform Block

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

def glsl_reflection(code, root_paths=[]):
    import tempfile, subprocess, json, platform
    
    GLSLParser = os.path.join(os.path.dirname(__file__), 'GLSLParser', '.bin', 'GLSLParser')
    
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(code.encode('utf-8'))
    tmp.close()

    command = f'"{GLSLParser}" "{tmp.name}"'
    if platform.system() == 'Windows':
        #run with utf8 code page to support non-ascii paths
        command = f'CHCP 65001 > nul && {command}'
    
    try:
        json_string = subprocess.check_output(command, shell=True)
    except:
        import stat
        os.chmod(GLSLParser, os.stat(GLSLParser).st_mode | stat.S_IEXEC)
        json_string = subprocess.check_output(command, shell=True)
    
    os.remove(tmp.name)
    
    reflection = json.loads(json_string)

    from Malt.GL.GLSLEval import glsl_eval

    for function in reflection['functions'].values():
        for parameter in function['parameters']:
            try:
                parameter['meta']['default'] = glsl_eval(parameter['meta']['default'])
            except:
                pass
    
    for struct in reflection['structs'].values():
        for member in struct['members']:
            try:
                member['meta']['default'] = glsl_eval(member['meta']['default'])
            except:
                pass

    def fix_paths(dic):
        for e in dic.values():
            path = e['file']
            path = os.path.normpath(path)
            for root_path in root_paths:
                try:
                    _path = os.path.relpath(e['file'], root_path)
                    if len(_path) < len(path):
                        path = _path
                except: pass
            e['file'] = path.replace('\\','/')
    
    fix_paths(reflection['structs'])
    fix_paths(reflection['functions'])

    functions = {}
    for key, function in reflection['functions'].items():
        new_key = function['file'].replace('/',' - ').replace('.glsl',' - ') + function['name']
        if function['name'].isupper() or function['name'].startswith('_'):
            new_key = function['name']
        if new_key not in functions.keys():
            functions[new_key] = []
        functions[new_key].append(function)
    reflection['functions'] = {}
    for key, functions in functions.items():
        if len(functions) == 1:
            reflection['functions'][key] = functions[0]
        else:
            for function in functions:
                new_key = key + ' - ' + function['signature']
                reflection['functions'][new_key] = function
    
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

