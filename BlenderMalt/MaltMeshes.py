# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import ctypes

import bpy

from .Malt.Mesh import Mesh
from .Malt import GL

__MESHES = {}

def get_mesh(object):
    key = object.name_full
    if key not in __MESHES.keys() or __MESHES[key] is None:
        __MESHES[key] = __load_mesh(object)
        
    return __MESHES[key]

def __load_mesh(object):
    m = object.to_mesh()
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
        normals = GL.gl_buffer(GL.GL_FLOAT, count*3)
        uvs = [GL.gl_buffer(GL.GL_FLOAT, count*2)] * len(m.uv_layers) if len(m.uv_layers) > 0 else []
        colors = [GL.gl_buffer(GL.GL_FLOAT, count*4)] * len(m.vertex_colors) if len(m.vertex_colors) > 0 else []
        
        position_indices = GL.gl_buffer(GL.GL_UNSIGNED_INT, count)
        positions = GL.gl_buffer(GL.GL_FLOAT, count*3)

        m.loop_triangles.foreach_get("loops",indices)
        m.loops.foreach_get("normal",normals)
        for i, uv_layer in enumerate(m.uv_layers):
            uv_layer.data.foreach_get("uv", uvs[i])
        for i, vertex_color in enumerate(m.vertex_colors):
            vertex_color.data.foreach_get("color", colors[i])
        
        m.loops.foreach_get("vertex_index",position_indices)

        #TODO: Use something faster
        for i in range(0,count):
            positions[i*3+0] = m.vertices[position_indices[i]].co[0]
            positions[i*3+1] = m.vertices[position_indices[i]].co[1]
            positions[i*3+2] = m.vertices[position_indices[i]].co[2]
        
        return Mesh(positions, indices, normals, uvs, colors)
        

@bpy.app.handlers.persistent
def depsgraph_update(scene, depsgraph):
    for update in depsgraph.updates:
        if update.is_updated_geometry:
            __MESHES[update.id.name_full] = None

def register():
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update)


def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update)

