import ctypes

from Malt.GL.GL import *

class Mesh():

    def __init__(self, position, index, normal=None, tangent=None, uvs=[], colors=[]):
        self.position = None
        self.normal = None
        self.tangent = None
        self.uvs = []
        self.colors = []

        self.index_count = len(index)

        self.VAO = None
        self.EBO = gl_buffer(GL_INT, 1)
        index_buffer = index
        #make sure it's an uint32 c array
        if isinstance(index_buffer, ctypes.Array) == False or index_buffer._type_ != ctypes.c_uint32:
            index_buffer = gl_buffer(GL_UNSIGNED_INT, len(index), index)
        glGenBuffers(1, self.EBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO[0])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(index_buffer) * 4, index_buffer, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        
        def load_VBO(data):
            #make sure it's a float c array
            if isinstance(data, ctypes.Array) == False or data._type_ != ctypes.c_float:
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
        if tangent:
            self.tangent = load_VBO(tangent)
        for uv in uvs:
            self.uvs.append(load_VBO(uv))
        for color in colors:
            self.colors.append(load_VBO(color))
    
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
        if(self.tangent):
            bind_VBO(self.tangent, 2, 4)
        
        max_uv = 4
        uv0_index = 3
        color0_index = uv0_index + max_uv
        for i, uv in enumerate(self.uvs):
            assert(i < max_uv)
            bind_VBO(uv, uv0_index + i, 2)
        for i, color in enumerate(self.colors):
            bind_VBO(color, color0_index + i, 4)

        glBindVertexArray(0)

    def bind(self):
        if self.VAO is None:
            self.__load_VAO()
        glBindVertexArray(self.VAO[0])
    
    def draw(self, bind=True):
        if bind:
            self.bind()
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, NULL)
        if bind:
            glBindVertexArray(0)
    
    def __del__(self):
        if self.VAO:
            glDeleteVertexArrays(1, self.VAO)
        
        def delete_buffer(buffer):
            if buffer:
                glDeleteBuffers(1, buffer)

        delete_buffer(self.EBO)
        delete_buffer(self.position)
        delete_buffer(self.normal)
        delete_buffer(self.tangent)
        for uv in self.uvs:
            delete_buffer(uv)
        for color in self.colors:
            delete_buffer(color)
            

#Class for custom mesh loading
#See Bridge/Mesh.py
class MeshCustomLoad(Mesh):

    def __init__(self):
        self.position = None
        self.normal = None
        self.tangent = None
        self.uvs = []
        self.colors = []

        self.index_count = 0

        self.VAO = None
        self.EBO = None
    

