from Malt.GL.GL import *
from Malt.GL import Mesh


class Texture():

    def __init__(self, resolution, internal_format=GL_RGB32F, data_format = None, data = NULL, 
        wrap=GL_CLAMP_TO_EDGE, min_filter=GL_LINEAR, mag_filter=GL_LINEAR, pixel_format=None, 
        build_mipmaps = False, anisotropy = False):
        
        self.resolution = resolution
        self.internal_format = internal_format
        self.format = pixel_format or internal_format_to_format(internal_format)
        self.data_format = data_format or internal_format_to_data_format(internal_format)
        self.channel_count = format_channels(self.format)
        self.channel_size = data_format_size(self.data_format)

        self.texture = gl_buffer(GL_INT, 1)
        glGenTextures(1, self.texture)

        glBindTexture(GL_TEXTURE_2D, self.texture[0])
        glTexImage2D(GL_TEXTURE_2D, 0, self.internal_format, resolution[0], resolution[1], 
            0, self.format, self.data_format, data)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mag_filter)
        
        if build_mipmaps:
            glGenerateMipmap(GL_TEXTURE_2D)
        if anisotropy:
            level = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY, level)

        glBindTexture(GL_TEXTURE_2D, 0)
    
    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture[0])
    
    def __del__(self):
        glDeleteTextures(1, self.texture)


class TextureArray():

    def __init__(self, resolution, length, internal_format=GL_RGB32F, data_format = GL_FLOAT, data = NULL, wrap=GL_CLAMP_TO_EDGE, min_filter=GL_LINEAR, mag_filter=GL_LINEAR):
        self.resolution = resolution
        self.internal_format = internal_format
        self.format = internal_format_to_format(internal_format)
        self.data_format = data_format
        self.length = length

        self.texture = gl_buffer(GL_INT, 1)
        glGenTextures(1, self.texture)

        glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture[0])
        glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, self.internal_format, resolution[0], resolution[1], length);
        '''
        glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, self.internal_format, resolution[0], resolution[1], length,
            0, self.format, self.data_format, data)
        '''
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, wrap)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, min_filter)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, mag_filter)

        glBindTexture(GL_TEXTURE_2D_ARRAY, 0)
    
    def bind(self):
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture[0])
    
    def __del__(self):
        glDeleteTextures(1, self.texture)


class CubeMap():

    def __init__(self, resolution, internal_format=GL_RGB32F, data_format = GL_FLOAT, data = [NULL]*6, min_filter=GL_LINEAR, mag_filter=GL_LINEAR):
        self.resolution = resolution
        self.internal_format = internal_format
        self.format = internal_format_to_format(internal_format)
        self.data_format = data_format

        self.texture = gl_buffer(GL_INT, 1)
        glGenTextures(1, self.texture)

        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture[0])
        
        for i in range(6):
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, self.internal_format, resolution[0], resolution[1], 
                0, self.format, self.data_format, NULL)
            #glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, min_filter)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, mag_filter)

        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
    
    def bind(self):
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture[0])
    
    def __del__(self):
        glDeleteTextures(1, self.texture)


class CubeMapArray():

    def __init__(self, resolution, length, internal_format=GL_RGB32F, data_format = GL_FLOAT, data = NULL, min_filter=GL_LINEAR, mag_filter=GL_LINEAR):
        self.resolution = resolution
        self.internal_format = internal_format
        self.format = internal_format_to_format(internal_format)
        self.data_format = data_format
        self.length = length

        self.texture = gl_buffer(GL_INT, 1)
        glGenTextures(1, self.texture)

        glBindTexture(GL_TEXTURE_CUBE_MAP_ARRAY, self.texture[0])
        glTexStorage3D(GL_TEXTURE_CUBE_MAP_ARRAY, 1, self.internal_format, resolution[0], resolution[1], length*6);
        '''
        glTexImage3D(GL_TEXTURE_CUBE_MAP_ARRAY, 0, self.internal_format, resolution[0], resolution[1], length,
            0, self.format, self.data_format, data)
        '''
        glTexParameteri(GL_TEXTURE_CUBE_MAP_ARRAY, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP_ARRAY, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP_ARRAY, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP_ARRAY, GL_TEXTURE_MIN_FILTER, min_filter)
        glTexParameteri(GL_TEXTURE_CUBE_MAP_ARRAY, GL_TEXTURE_MAG_FILTER, mag_filter)

        glBindTexture(GL_TEXTURE_CUBE_MAP_ARRAY, 0)
    
    def bind(self):
        glBindTexture(GL_TEXTURE_CUBE_MAP_ARRAY, self.texture[0])
    
    def __del__(self):
        glDeleteTextures(1, self.texture)


class Gradient():

    def __init__(self, data, resolution, internal_format=GL_RGBA32F, data_format = GL_FLOAT, nearest_interpolation = False):
        self.resolution = resolution
        self.internal_format = internal_format
        self.format = internal_format_to_format(internal_format)
        self.data_format = data_format

        self.texture = gl_buffer(GL_INT, 1)
        glGenTextures(1, self.texture)

        glBindTexture(GL_TEXTURE_1D, self.texture[0])
        glTexImage1D(GL_TEXTURE_1D, 0, self.internal_format, resolution, 0, self.format, self.data_format, data)
        #glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        interpolation = GL_NEAREST if nearest_interpolation else GL_LINEAR
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, interpolation)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, interpolation)

        glBindTexture(GL_TEXTURE_1D, 0)
    
    def bind(self):
        glBindTexture(GL_TEXTURE_1D, self.texture[0])
    
    def __del__(self):
        glDeleteTextures(1, self.texture)


def internal_format_to_data_format(internal_format):
    name = GL_ENUMS[internal_format]
    table = {
        'F' : GL_FLOAT,
        'UI' : GL_UNSIGNED_INT,
        'I' : GL_INT,
    }
    for key, value in table.items():
        if name.endswith(key):
            return value
    return GL_UNSIGNED_BYTE

def data_format_size(data_format):
    name = GL_ENUMS[data_format]
    table = {
        'BYTE' : 1,
        'SHORT' : 2,
        'HALF' : 2,
    }
    for key, value in table.items():
        if key in name:
            return value
    return 4

def internal_format_to_sampler_type(internal_format):
    table = {
        GL_UNSIGNED_BYTE : 'sampler2D',
        GL_FLOAT : 'sampler2D',
        GL_INT : 'isampler2D',
        GL_UNSIGNED_INT : 'usampler2D'
    }
    return table[internal_format_to_data_format(internal_format)]

def internal_format_to_vector_type(internal_format):
    table = {
        'sampler2D' : 'vec4',
        'isampler2D' : 'ivec4',
        'usampler2D' : 'uvec4',
    }
    return table[internal_format_to_sampler_type(internal_format)]

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
            if name.endswith('I'):
                return GL_NAMES[GL_ENUMS[value] + '_INTEGER']
            else:
                return value
    raise Exception(name, ' Texture format not supported')

def format_channels(format):
    table = {
        GL_RGBA : 4,
        GL_RGB : 3,
        GL_RG : 2,
        GL_RED : 1,
    }
    if format in table.keys():
        return table[format]
    return 1

    


