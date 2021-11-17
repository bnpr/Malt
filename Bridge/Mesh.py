# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 
from Malt.Utils import LOG

from Malt.GL import Mesh
from Malt.GL.GL import *

MESHES = {}

def load_mesh(msg):
    name = msg['name']
    data = msg['data']
    MESHES[name] = []

    def load_VBO(data):
        VBO = gl_buffer(GL_INT, 1)
        glGenBuffers(1, VBO)
        glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
        glBufferData(GL_ARRAY_BUFFER, data.size_in_bytes(), data.buffer(), GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        return VBO

    positions = load_VBO(data['positions'])
    normals = load_VBO(data['normals'])
    tangents = load_VBO(data['tangents']) if data['tangents'] else None
    uvs = [load_VBO(e) for e in data['uvs']]
    colors = [load_VBO(e) for e in data['colors']]

    for i, indices in enumerate(data['indices']):
        result = Mesh.MeshCustomLoad()
        
        result.VAO = gl_buffer(GL_INT, 1)
        glGenVertexArrays(1, result.VAO)
        glBindVertexArray(result.VAO[0])
        
        result.EBO = gl_buffer(GL_INT, 1)
        glGenBuffers(1, result.EBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, result.EBO[0])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size_in_bytes(), indices.buffer(), GL_STATIC_DRAW)
        
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
        if data['positions'].size_in_bytes() == data['normals'].size_in_bytes():
            bind_VBO(result.normal, 1, 3)
        else:
            bind_VBO(result.normal, 1, 3, GL_SHORT, GL_TRUE)
        
        if tangents:
            bind_VBO(tangents, 2, 4)
        
        max_uv = 4
        max_vertex_colors = 4
        uv0_index = 3
        color0_index = uv0_index + max_uv
        for i, uv in enumerate(result.uvs):
            if i >= max_uv:
                LOG.warning('{} : UV count exceeds max supported UVs ({})'.format(name, max_uv))
                break
            bind_VBO(uv, uv0_index + i, 2)
        for i, color in enumerate(result.colors):
            if i >= max_vertex_colors:
                LOG.warning('{} : Vertex Color Layer count exceeds max supported layers ({})'.format(name, max_uv))
                break
            bind_VBO(color, color0_index + i, 4, GL_UNSIGNED_BYTE, GL_TRUE)

        glBindVertexArray(0)
        
        MESHES[name].append(result)


