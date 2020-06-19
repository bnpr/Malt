# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

from .GL import *

class Mesh(object):

    def __init__(self, position, index, normal=None, uvs={}, colors={}):
        self.position = None
        self.normal = None
        self.uvs = {}
        self.colors = {}

        self.index_count = len(index)

        self.VAO = None
        self.EBO = gl_buffer(GL_INT, 1)
        index_buffer = gl_buffer(GL_UNSIGNED_INT, len(index), index)
        glGenBuffers(1, self.EBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO[0])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(index_buffer) * 4, index_buffer, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        
        def load_VBO(data):
            data = gl_buffer(GL_FLOAT, len(data), data)
            VBO = gl_buffer(GL_INT, 1)
            glGenBuffers(1, VBO)
            glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
            glBufferData(GL_ARRAY_BUFFER, len(data) * 4, data, GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            return VBO
        
        self.position = load_VBO(position)
        if normal:
            self.normal = load_VBO(normal)
        for key, value in uvs.items():
            self.uvs[key] = load_VBO(value)
        for key, value in colors.items():
            self.colors[key] = load_VBO(value)
    
    #Blender uses different OGL contexts, this function should only be called from the draw callback
    #https://developer.blender.org/T65208
    def __load_VAO(self):
        self.VAO = gl_buffer(GL_INT, 1)
        glGenVertexArrays(1, self.VAO)
        glBindVertexArray(self.VAO[0])

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO[0])

        def bind_VBO(VBO, index, element_size):
            glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
            glEnableVertexAttribArray(index)
            glVertexAttribPointer(index, element_size, GL_FLOAT, GL_FALSE, 0, None)
        
        bind_VBO(self.position, 0, 3)
        if(self.normal):
            bind_VBO(self.normal, 1, 3)
        
        uv0_index = 2
        color0_index = 10
        for key, value in self.uvs.items():
            assert(uv0_index + key < color0_index)
            bind_VBO(value, uv0_index + key, 2)
        for key, value in self.colors.items():
            bind_VBO(value, color0_index + key, 4)

        glBindVertexArray(0)

    def bind(self):
        if self.VAO is None:
            self.__load_VAO()
        glBindVertexArray(self.VAO[0])
    
    def draw(self):
        self.bind()
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, NULL)
        glBindVertexArray(0)
    
    def __del__(self):
        #WARNING: There's no warranty this wil be deleted in the correct OGL context ???
        def delete_buffer(buffer):
            if buffer:
                glDeleteBuffers(1, buffer)

        delete_buffer(self.EBO)
        delete_buffer(self.position)
        delete_buffer(self.normal)
        for key, value in self.uvs.items():
            delete_buffer(value)
        for key, value in self.colors.items():
            delete_buffer(value)
        if self.VAO:
            glDeleteVertexArrays(1, self.VAO)
            
