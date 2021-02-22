# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import ctypes, array

import bpy

from BlenderMalt import MaltPipeline
from . import CBlenderMalt

MESHES = {}

def get_mesh_name(object):
    name = object.name_full
    if len(object.modifiers) == 0 and object.data:
        name = object.type + '_' + object.data.name_full
    return name

def get_mesh(object):
    key = get_mesh_name(object)
    if key not in MESHES.keys() or MESHES[key] is None:
        MESHES[key] = load_mesh(object)
    return MESHES[key]

def load_mesh(object):
    use_split_faces = False #Use split_faces instead of calc_normals_split (Slightly faster)

    m = object.data
    if object.type != 'MESH' or bpy.context.mode == 'EDIT_MESH':
        m = object.to_mesh()
    
    if m is None or len(m.polygons) == 0:
        return None
    
    m.calc_loop_triangles()

    polys_ptr = ctypes.c_void_p(m.polygons[0].as_pointer())
    has_flat_polys = CBlenderMalt.has_flat_polys(polys_ptr, len(m.polygons))

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

    CBlenderMalt.retrieve_mesh_data(verts_ptr, loops_ptr, loop_count, loop_tris_ptr, loop_tri_count, polys_ptr,
        positions, normals, indices_ptrs, indices_lengths)

    if needs_split_normals and use_split_faces == False:
        #TODO: Find a way to get a direct pointer to custom normals
        normals = retrieve_array(m.loops, 'normal', 'f', ctypes.c_float, [0.0,0.0,0.0])    

    uvs = []
    tangents = []
    for i, uv_layer in enumerate(m.uv_layers):
        uv_ptr = ctypes.c_void_p(uv_layer.data[0].as_pointer())
        uv = get_load_buffer('uv'+str(i), ctypes.c_float, loop_count * 2)
        CBlenderMalt.retrieve_mesh_uv(uv_ptr, loop_count, uv)
        uvs.append(uv)

        if(object.original.data.malt_parameters.bools['precomputed_tangents'].boolean):
            m.calc_tangents(uvmap=uv_layer.name)
            #calc_tangents is so slow there's no point in optimizing this
            packed_tangents = [e for l in m.loops for e in (*l.tangent, l.bitangent_sign)]
            tangents.append(packed_tangents)

    colors = []
    for i, vertex_color in enumerate(m.vertex_colors):
        #Colors are already contiguous in memory, so we pass them directly to OpenGL
        color = (ctypes.c_uint8 * (loop_count * 4)).from_address(vertex_color.data[0].as_pointer())
        colors.append(color)
    
    #TODO: Optimize. Create load buffers from bytearrays and retrieve them later
    mesh_data = {
        'positions': bytearray(positions),
        'indices': [bytearray(i) for i in indices],
        'indices_lengths': [l for l in indices_lengths],
        'normals': bytearray(normals),
        'uvs': [bytearray(u) for u in uvs],
        'tangents': [bytearray(t) for t in tangents],
        'colors': [bytearray(c) for c in colors],
    }

    name = get_mesh_name(object)

    MaltPipeline.get_bridge().load_mesh(name, mesh_data)

    return [name for i in range(material_count)]

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

def unload_mesh(object):
    MESHES[get_mesh_name(object)] = None

def reset_meshes():
    global MESHES
    MESHES = {}    

def register():
    pass

def unregister():
    pass

