# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from Malt.GL import *

class Texture(object):

    def __init__(self, resolution, internal_format=GL_RGB32F, data_format = GL_FLOAT, data = NULL, wrap=GL_CLAMP_TO_EDGE, min_filter=GL_LINEAR, mag_filter=GL_LINEAR):
        self.resolution = resolution
        self.internal_format = internal_format
        self.format = internal_format_to_format(internal_format)
        self.data_format = data_format

        self.texture = gl_buffer(GL_INT, 1)
        glGenTextures(1, self.texture)

        glBindTexture(GL_TEXTURE_2D, self.texture[0])
        glTexImage2D(GL_TEXTURE_2D, 0, self.internal_format, resolution[0], resolution[1], 
            0, self.format, self.data_format, data)
        #glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mag_filter)

        glBindTexture(GL_TEXTURE_2D, 0)
    
    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture[0])
    
    def __del__(self):
        try:
            glDeleteTextures(1, self.texture)
        except:
            #TODO: Make sure GL objects are deleted in the correct context
            pass


class TextureArray(object):

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
        try:
            glDeleteTextures(1, self.texture)
        except:
            #TODO: Make sure GL objects are deleted in the correct context
            pass


class CubeMap(object):

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
        try:
            glDeleteTextures(1, self.texture)
        except:
            #TODO: Make sure GL objects are deleted in the correct context
            pass

class CubeMapArray(object):

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
        try:
            glDeleteTextures(1, self.texture)
        except:
            #TODO: Make sure GL objects are deleted in the correct context
            pass



class Gradient(object):

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
        try:
            glDeleteTextures(1, self.texture)
        except:
            #TODO: Make sure GL objects are deleted in the correct context
            pass
