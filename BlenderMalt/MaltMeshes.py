# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import ctypes
import itertools

import numpy as np
import array

import bpy

from Malt.Mesh import MeshCustomLoad
from Malt.GL import *
from Malt.Utils import log

import CMalt

MESHES = {}

def get_mesh(object):
    key = object.name_full
    if key not in MESHES.keys() or MESHES[key] is None:
        MESHES[key] = load_mesh(object)
        
    return MESHES[key]

def load_mesh(object):
    precomputed_tangents = False
    use_split_faces = False #Use split_faces instead of calc_normals_split (Slightly faster)

    m = object.data
    if object.type != 'MESH' or bpy.context.mode == 'EDIT_MESH':
        m = object.to_mesh()
    
    if m is None:
        return None
    
    m.calc_loop_triangles()

    polys_ptr = ctypes.c_void_p(m.polygons[0].as_pointer())
    has_flat_polys = CMalt.has_flat_polys(polys_ptr, len(m.polygons))

    needs_split_normals = m.use_auto_smooth or m.has_custom_normals or has_flat_polys
    if needs_split_normals:
        if use_split_faces:
            m.split_faces()
        else:
            m.calc_normals_split()

    verts_ptr = ctypes.c_void_p(m.vertices[0].as_pointer())
    loops_ptr = ctypes.c_void_p(m.loops[0].as_pointer())
    loop_tris_ptr = ctypes.c_void_p(m.loop_triangles[0].as_pointer())

    loop_count = len(m.loops)
    loop_tri_count = len(m.loop_triangles)
    material_count = max(1, len(m.materials))

    positions = get_load_buffer('positions', ctypes.c_float, (loop_count * 3))
    normals = get_load_buffer('normals', ctypes.c_int16, (loop_count * 3))
    indices = []
    indices_ptrs = (ctypes.c_void_p * material_count)()
    for i in range(material_count):
        indices.append(get_load_buffer('indices'+str(i), ctypes.c_uint32, (loop_tri_count * 3)))
        indices_ptrs[i] = ctypes.cast(indices[i], ctypes.c_void_p)
    
    #Create a new one each time so we don't have to care about zeroing the previous results
    indices_lengths = (ctypes.c_uint32 * material_count)()

    CMalt.retrieve_mesh_data(verts_ptr, loops_ptr, loop_count, loop_tris_ptr, loop_tri_count, polys_ptr,
        positions, normals, indices_ptrs, indices_lengths)
    
    def load_VBO(data):
        VBO = gl_buffer(GL_INT, 1)
        glGenBuffers(1, VBO)
        glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
        glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(data), data, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        return VBO

    positions = load_VBO(positions)
    
    if needs_split_normals and use_split_faces == False:
        #TODO: Find a way to get a direct pointer to custom normals
        normals = retrieve_array(m.loops, 'normal', 'f', ctypes.c_float, [0.0,0.0,0.0])
    
    normals = load_VBO(normals)
    
    EBOs = []
    for i in range(material_count):
        EBO = gl_buffer(GL_INT, 1)
        glGenBuffers(1, EBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO[0])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_lengths[i] * 4, indices[i], GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        EBOs.append(EBO)
    
    uvs = []
    tangents = []
    for i, uv_layer in enumerate(m.uv_layers):
        uv_ptr = ctypes.c_void_p(uv_layer.data[0].as_pointer())
        uv = get_load_buffer('uv'+str(i), ctypes.c_float, loop_count * 2)
        CMalt.retrieve_mesh_uv(uv_ptr, loop_count, uv)
        uvs.append(load_VBO(uv))

        if(precomputed_tangents):
            m.calc_tangents(uvmap=uv_layer.name)
            #calc_tangents is so slow there's no point in optimizing this
            packed_tangents = [e for l in m.loops for e in (*l.tangent, l.bitangent_sign)]
            packed_tangents = (ctypes.c_float * (4*len(packed_tangents)))(packed_tangents)
            tangents.append(load_VBO(packed_tangents))

    colors = []
    for i, vertex_color in enumerate(m.vertex_colors):
        #Colors are already contiguous in memory, so we pass them directly to OpenGL
        color = (ctypes.c_uint8 * (loop_count * 4)).from_address(vertex_color.data[0].as_pointer())
        colors.append(load_VBO(color))
    
    results = []

    for i in range(material_count):
        result = MeshCustomLoad()
        
        result.EBO = EBOs[i]
        result.index_count = indices_lengths[i]
        result.position = positions
        result.normal = normals
        result.uvs = uvs
        result.tangents = tangents
        result.colors = colors

        result.VAO = gl_buffer(GL_INT, 1)
        glGenVertexArrays(1, result.VAO)
        glBindVertexArray(result.VAO[0])

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, result.EBO[0])

        def bind_VBO(VBO, index, element_size, gl_type=GL_FLOAT, gl_normalize=GL_FALSE):
            glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
            glEnableVertexAttribArray(index)
            glVertexAttribPointer(index, element_size, gl_type, gl_normalize, 0, None)
        
        bind_VBO(result.position, 0, 3)
        if needs_split_normals and use_split_faces == False:
            bind_VBO(result.normal, 1, 3)
        else:
            bind_VBO(result.normal, 1, 3, GL_SHORT, GL_TRUE)
        
        max_uv = 4
        tangent0_index = 2
        uv0_index = tangent0_index + max_uv
        color0_index = uv0_index + max_uv
        for i, tangent in enumerate(result.tangents):
            assert(i < max_uv)
            bind_VBO(tangent, tangent0_index + i, 4)
        for i, uv in enumerate(result.uvs):
            assert(i < max_uv)
            bind_VBO(uv, uv0_index + i, 2)
        for i, color in enumerate(result.colors):
            bind_VBO(color, color0_index + i, 4, GL_UNSIGNED_BYTE, GL_TRUE)

        glBindVertexArray(0)
        
        results.append(result)

    return results

#Reuse load buffers to avoid new allocations
buffers = {}
def get_load_buffer(name, ctype, size):
    if name not in buffers or size > len(buffers[name]):
        buffers[name] = (ctype * size)()
    assert(buffers[name]._type_ == ctype)
    return (ctype * size).from_address(ctypes.addressof(buffers[name]))

def retrieve_array(bpy_array, property_name, array_format, ctype_format, default_value):
    #foreach_get only uses memcpy on python array.array, so even with the allocation cost they are faster than ctypes arrays
    result = array.array(array_format, [default_value[0]]) * (len(bpy_array)*len(default_value))
    bpy_array.foreach_get(property_name, result)
    result = (ctype_format*len(result)).from_buffer(result)
    return result

@bpy.app.handlers.persistent
def reset_meshes(dummy):
    global MESHES
    MESHES = {}    

@bpy.app.handlers.persistent
def depsgraph_update(scene, depsgraph):
    for update in depsgraph.updates:
        if update.is_updated_geometry:
            MESHES[update.id.name_full] = None

def register():
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update)
    bpy.app.handlers.load_post.append(reset_meshes)

def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update)
    bpy.app.handlers.load_post.remove(reset_meshes)

