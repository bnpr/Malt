# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 
import logging as log

from Malt.GL import Mesh
from Malt.GL.GL import *

MESHES = {}

def load_mesh(msg):
    name = msg['name']
    data = msg['data']
    MESHES[name] = []

    def load_VBO(data):
        #Cast from bytearray to ctypes, otherwise it breaks on Linux. IDKW
        data = (ctypes.c_float * (len(data)//4)).from_buffer(data)
        VBO = gl_buffer(GL_INT, 1)
        glGenBuffers(1, VBO)
        glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
        glBufferData(GL_ARRAY_BUFFER, len(data)*4, data, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        return VBO

    positions = load_VBO(data['positions'])
    normals = load_VBO(data['normals'])
    uvs = [load_VBO(e) for e in data['uvs']]
    tangents = [load_VBO(e) for e in data['tangents']]
    colors = [load_VBO(e) for e in data['colors']]

    for i, indices in enumerate(data['indices']):
        result = Mesh.MeshCustomLoad()
        
        result.VAO = gl_buffer(GL_INT, 1)
        glGenVertexArrays(1, result.VAO)
        glBindVertexArray(result.VAO[0])
        
        #Cast from bytearray to ctypes, otherwise it breaks on Linux. IDKW
        indices = (ctypes.c_uint32 * (len(indices)//4)).from_buffer(indices)
        result.EBO = gl_buffer(GL_INT, 1)
        glGenBuffers(1, result.EBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, result.EBO[0])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices)*4, indices, GL_STATIC_DRAW)
        
        result.index_count = data['indices_lengths'][i]

        result.position = positions
        result.normal = normals
        result.uvs = uvs
        result.tangents = tangents
        result.colors = colors

        def bind_VBO(VBO, index, element_size, gl_type=GL_FLOAT, gl_normalize=GL_FALSE):
            glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
            glEnableVertexAttribArray(index)
            glVertexAttribPointer(index, element_size, gl_type, gl_normalize, 0, None)
        
        bind_VBO(result.position, 0, 3)
        if len(data['positions']) == len(data['normals']):
            bind_VBO(result.normal, 1, 3)
        else:
            bind_VBO(result.normal, 1, 3, GL_SHORT, GL_TRUE)
        
        max_uv = 4
        max_vertex_colors = 4
        tangent0_index = 2
        uv0_index = tangent0_index + max_uv
        color0_index = uv0_index + max_uv
        for i, tangent in enumerate(result.tangents):
            if i >= max_uv:
                break
            bind_VBO(tangent, tangent0_index + i, 4)
        for i, uv in enumerate(result.uvs):
            if i >= max_uv:
                log.warning('{} : UV count exceeds max supported UVs ({})'.format(name, max_uv))
                break
            bind_VBO(uv, uv0_index + i, 2)
        for i, color in enumerate(result.colors):
            if i >= max_vertex_colors:
                log.warning('{} : Vertex Color Layer count exceeds max supported layers ({})'.format(name, max_uv))
                break
            bind_VBO(color, color0_index + i, 4, GL_UNSIGNED_BYTE, GL_TRUE)

        glBindVertexArray(0)
        
        MESHES[name].append(result)


