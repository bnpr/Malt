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

    m = object.data
    if object.type != 'MESH' or bpy.context.mode == 'EDIT_MESH':
        m = object.to_mesh()
    
    if m is None or len(m.polygons) == 0:
        return None
    
    m.calc_loop_triangles()
    m.calc_normals_split()
    
    mesh_ptr = ctypes.c_void_p(m.as_pointer())
    loop_tris_ptr = ctypes.c_void_p(m.loop_triangles[0].as_pointer())

    loop_count = len(m.loops)
    loop_tri_count = len(m.loop_triangles)
    material_count = max(1, len(m.materials))

    positions = get_load_buffer('positions', ctypes.c_float, (loop_count * 3))
    normals = get_load_buffer('normals', ctypes.c_float, (loop_count * 3))
    indices = []
    indices_ptrs = (ctypes.c_void_p * material_count)()
    for i in range(material_count):
        indices.append(get_load_buffer('indices'+str(i), ctypes.c_uint32, (loop_tri_count * 3)))
        indices_ptrs[i] = ctypes.cast(indices[i].buffer(), ctypes.c_void_p)
    
    indices_lengths = (ctypes.c_uint32 * material_count)()

    CBlenderMalt.retrieve_mesh_data(mesh_ptr, loop_tris_ptr, loop_tri_count,
        positions.buffer(), normals.buffer(), indices_ptrs, indices_lengths)
    
    for i in range(material_count):
        indices[i]._size = indices_lengths[i]

    uvs_list = []
    tangents_buffer = None
    for i, uv_layer in enumerate(m.uv_layers):
        if i >= 4: break
        uv_ptr = ctypes.c_void_p(uv_layer.data[0].as_pointer())
        uv = get_load_buffer('uv'+str(i), ctypes.c_float, loop_count * 2)
        CBlenderMalt.retrieve_mesh_uv(uv_ptr, loop_count, uv.buffer())
        uvs_list.append(uv)
        if i == 0 and object.original.data.malt_parameters.bools['precomputed_tangents'].boolean:
            m.calc_tangents(uvmap=uv_layer.name)
            tangents_ptr = CBlenderMalt.mesh_tangents_ptr(ctypes.c_void_p(m.as_pointer()))
            tangents = (ctypes.c_float * (loop_count * 4)).from_address(ctypes.addressof(tangents_ptr.contents))
            tangents_buffer = get_load_buffer('tangents'+str(i), ctypes.c_float, (loop_count * 4))
            ctypes.memmove(tangents_buffer.buffer(), tangents, tangents_buffer.size_in_bytes())
    
    colors_list = [None]*4
    for i, vertex_color in enumerate(m.vertex_colors):
        if i >= 4: break
        color = (ctypes.c_uint8 * (loop_count * 4)).from_address(vertex_color.data[0].as_pointer())
        color_buffer = get_load_buffer('colors'+str(i), ctypes.c_uint8, loop_count*4)
        ctypes.memmove(color_buffer.buffer(), color, color_buffer.size_in_bytes())
        colors_list[i] = color_buffer
    
    if object.type == 'MESH':
        for i in range(4):
            try:
                override = getattr(object.original.data, f'malt_vertex_color_override_{i}')
                attribute = m.attributes.get(override)
                if attribute and attribute.domain == 'CORNER' and attribute.data_type == 'FLOAT_COLOR':
                    color = (ctypes.c_float * (loop_count * 4)).from_address(attribute.data[0].as_pointer())
                    color_buffer = get_load_buffer('colors_override'+str(i), ctypes.c_float, loop_count*4)
                    ctypes.memmove(color_buffer.buffer(), color, color_buffer.size_in_bytes())
                    colors_list[i] = color_buffer
            except:
                import traceback
                traceback.print_exc()

    #TODO: Optimize. Create load buffers from bytearrays and retrieve them later
    mesh_data = {
        'positions': positions,
        'indices': indices,
        'normals': normals,
        'uvs': uvs_list,
        'tangents': tangents_buffer,
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

class MALT_PT_Attributes(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    bl_label = "Malt Vertex Color Overrides"
    COMPAT_ENGINES = {'MALT'}

    @classmethod
    def get_malt_property_owner(cls, context):
        if context.object and context.object.data and context.object.type == 'MESH':
            return context.object.data
    
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT' and cls.get_malt_property_owner(context)
    
    def draw(self, context):
        owner = self.get_malt_property_owner(context)
        if owner:
            self.layout.use_property_split = True
            self.layout.use_property_decorate = False  # No animation.
            self.layout.active = owner.library is None #Only local data can be edited
            self.layout.prop(owner, 'malt_vertex_color_override_0')    
            self.layout.prop(owner, 'malt_vertex_color_override_1')    
            self.layout.prop(owner, 'malt_vertex_color_override_2')    
            self.layout.prop(owner, 'malt_vertex_color_override_3')    

def register():
    bpy.types.Mesh.malt_vertex_color_override_0 = bpy.props.StringProperty(name='0')
    bpy.types.Mesh.malt_vertex_color_override_1 = bpy.props.StringProperty(name='1')
    bpy.types.Mesh.malt_vertex_color_override_2 = bpy.props.StringProperty(name='2')
    bpy.types.Mesh.malt_vertex_color_override_3 = bpy.props.StringProperty(name='3')
    bpy.utils.register_class(MALT_PT_Attributes)


def unregister():
    bpy.utils.unregister_class(MALT_PT_Attributes)
    del bpy.types.Mesh.malt_vertex_color_override_0
    del bpy.types.Mesh.malt_vertex_color_override_1
    del bpy.types.Mesh.malt_vertex_color_override_2
    del bpy.types.Mesh.malt_vertex_color_override_3

