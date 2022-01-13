import ctypes
import bpy

MESHES = {}

def get_mesh_name(object):
    name = object.name_full
    if len(object.modifiers) == 0 and object.data:
        name = object.type + '_' + object.data.name_full
    return name

def get_mesh(object):
    key = get_mesh_name(object)
    if key not in MESHES.keys() or MESHES[key] is None:
        MESHES[key] = load_mesh(object, key)
    return MESHES[key]

def load_mesh(object, name):
    from . import CBlenderMalt
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
        indices_ptrs[i] = ctypes.cast(indices[i].buffer(), ctypes.c_void_p)
    
    indices_lengths = (ctypes.c_uint32 * material_count)()

    CBlenderMalt.retrieve_mesh_data(verts_ptr, loops_ptr, loop_count, loop_tris_ptr, loop_tri_count, polys_ptr,
        positions.buffer(), normals.buffer(), indices_ptrs, indices_lengths)

    if needs_split_normals and use_split_faces == False:
        #TODO: Find a way to get a direct pointer to custom normals
        normals = get_load_buffer('custom_normals', ctypes.c_float, (loop_count * 3))
        m.loops.foreach_get('normal', normals.as_np_array())

    uvs_list = []
    tangents = None
    for i, uv_layer in enumerate(m.uv_layers):
        uv_ptr = ctypes.c_void_p(uv_layer.data[0].as_pointer())
        uv = get_load_buffer('uv'+str(i), ctypes.c_float, loop_count * 2)
        CBlenderMalt.retrieve_mesh_uv(uv_ptr, loop_count, uv.buffer())
        uvs_list.append(uv)
        if i == 0 and object.original.data.malt_parameters.bools['precomputed_tangents'].boolean:
            m.calc_tangents(uvmap=uv_layer.name)
            #TODO: Find a way to get a direct pointer
            tangents = get_load_buffer('tangents'+str(i), ctypes.c_float, (loop_count * 3))
            bitangent_signs = get_load_buffer('bitangent_signs'+str(i), ctypes.c_float, loop_count)
            m.loops.foreach_get('tangent', tangents.as_np_array())
            m.loops.foreach_get('bitangent_sign', bitangent_signs.as_np_array())
            packed_tangents = get_load_buffer('packed_tangents'+str(i), ctypes.c_float, (loop_count * 4))
            CBlenderMalt.pack_tangents(tangents.buffer(), bitangent_signs.buffer(), loop_count, packed_tangents.buffer())
            tangents = packed_tangents
    
    colors_list = []
    for i, vertex_color in enumerate(m.vertex_colors):
        color = (ctypes.c_uint8 * (loop_count * 4)).from_address(vertex_color.data[0].as_pointer())
        color_buffer = get_load_buffer('colors'+str(i), ctypes.c_uint8, loop_count*4)
        ctypes.memmove(color_buffer.buffer(), color, color_buffer.size_in_bytes())
        colors_list.append(color_buffer)
    
    #TODO: Optimize. Create load buffers from bytearrays and retrieve them later
    mesh_data = {
        'positions': positions,
        'indices': indices,
        'indices_lengths': [l for l in indices_lengths],
        'normals': normals,
        'uvs': uvs_list,
        'tangents': tangents,
        'colors': colors_list,
    }

    from . import MaltPipeline
    MaltPipeline.get_bridge().load_mesh(name, mesh_data)

    from Bridge.Proxys import MeshProxy
    return [MeshProxy(name, i) for i in range(material_count)]

def get_load_buffer(name, ctype, size):
    from . import MaltPipeline
    return MaltPipeline.get_bridge().get_shared_buffer(ctype, size)

def unload_mesh(object):
    MESHES[get_mesh_name(object)] = None

def reset_meshes():
    global MESHES
    MESHES = {}    

def register():
    pass

def unregister():
    pass

