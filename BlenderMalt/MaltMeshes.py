# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import ctypes
import itertools

import bpy

from Malt.Mesh import Mesh
from Malt import GL

MESHES = {}

def get_mesh(object):
    key = object.name_full
    if key not in MESHES.keys() or MESHES[key] is None:
        MESHES[key] = load_mesh(object)
        
    return MESHES[key]

def load_mesh(object):
    m = object.to_mesh()
    if m is None:
        return None

    m.calc_loop_triangles()
    m.calc_normals_split()

    #TODO: Blender indexes vertex positions and normals, but not uvs and colors,
    #we might need to do our own indexing or don't do indexing at all
    fast_path = False
    if fast_path:
        positions = (ctypes.c_float*(len(m.vertices)*3))()
        m.vertices.foreach_get("co", positions)
        normals = (ctypes.c_float*(len(m.vertices)*3))()
        m.vertices.foreach_get("normal", normals)
        indices = (ctypes.c_uint32*(len(m.loop_triangles)*3))()
        m.loop_triangles.foreach_get("vertices", indices)

        return Mesh(positions, indices, normals)
    else:    
        count = len(m.loops)

        indices = GL.gl_buffer(GL.GL_UNSIGNED_INT, len(m.loop_triangles)*3)
        m.loop_triangles.foreach_get("loops",indices)

        normals = GL.gl_buffer(GL.GL_FLOAT, count*3)
        m.loops.foreach_get("normal",normals)

        uvs = []
        tangents = []
        for i, uv_layer in enumerate(m.uv_layers):
            uvs.append(GL.gl_buffer(GL.GL_FLOAT, count*2))
            uv_layer.data.foreach_get("uv", uvs[i])

            try:
                m.calc_tangents(uvmap=uv_layer.name)
            except Exception as ex:
                # TODO:
                print("WARNING : Object :", object.name)
                print(ex)
            packed_tangents = [e for l in m.loops for e in (*l.tangent, l.bitangent_sign)]
            tangents.append(GL.gl_buffer(GL.GL_FLOAT, count*4, packed_tangents))

        colors = []
        for i, vertex_color in enumerate(m.vertex_colors):
            colors.append(GL.gl_buffer(GL.GL_FLOAT, count*4))
            vertex_color.data.foreach_get("color", colors[i])

        pos = [axis for l in m.loops for axis in m.vertices[l.vertex_index].co]
        positions = GL.gl_buffer(GL.GL_FLOAT, count*3, pos)

        return Mesh(positions, indices, normals, tangents, uvs, colors)

@bpy.app.handlers.persistent
def reset_meshes(dummy):
    global MESHES
    MESHES = {}    

def register():
    bpy.app.handlers.load_post.append(reset_meshes)

def unregister():
    bpy.app.handlers.load_post.remove(reset_meshes)

