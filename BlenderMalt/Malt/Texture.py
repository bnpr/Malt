# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from .GL import *

class Texture(object):

    def __init__(self, resolution, internal_format=GL_RGB32F, data_format = GL_FLOAT, data = NULL, wrap=GL_REPEAT, min_filter=GL_LINEAR, mag_filter=GL_LINEAR):
        self.resolution = resolution
        self.internal_format = internal_format
        self.format = internal_format_to_format(internal_format)

        self.texture = gl_buffer(GL_INT, 1)
        glGenTextures(1, self.texture)

        glBindTexture(GL_TEXTURE_2D, self.texture[0])
        glTexImage2D(GL_TEXTURE_2D, 0, self.internal_format, resolution[0], resolution[1], 
            0, self.format, data_format, data)
        #glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mag_filter)

        glBindTexture(GL_TEXTURE_2D, 0)
    
    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture[0])
    
    def __del__(self):
        glDeleteTextures(1, self.texture)


class Gradient(object):

    def __init__(self, data, resolution, internal_format=GL_RGBA32F, data_format = GL_FLOAT):
        self.resolution = resolution
        self.internal_format = internal_format
        self.format = internal_format_to_format(internal_format)

        self.texture = gl_buffer(GL_INT, 1)
        glGenTextures(1, self.texture)

        glBindTexture(GL_TEXTURE_1D, self.texture[0])
        glTexImage1D(GL_TEXTURE_1D, 0, self.internal_format, resolution, 0, self.format, data_format, data)
        #glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glBindTexture(GL_TEXTURE_1D, 0)
    
    def bind(self):
        glBindTexture(GL_TEXTURE_1D, self.texture[0])
    
    def __del__(self):
        glDeleteTextures(1, self.texture)
