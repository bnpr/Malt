# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from Malt.GL import *
from Malt.Utils import log

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

