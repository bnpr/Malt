# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from .GL import *

import ctypes

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

    def bind(self, location):
        glBindBufferRange(GL_UNIFORM_BUFFER, location, self.buffer[0], 0, self.size)
    
    def __del__(self):
        try:
            glDeleteBuffers(1, self.buffer[0])
        except:
            #TODO: Make sure GL objects are deleted in the correct context
            pass

