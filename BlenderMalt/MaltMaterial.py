import os
import bpy
from BlenderMalt.MaltUtils import malt_path_getter, malt_path_setter
from . MaltProperties import MaltPropertyGroup

_MATERIALS = {}

class MaltMaterial(bpy.types.PropertyGroup):

    def update_source(self, context):
        path = self.get_source_path()
        if path in _MATERIALS.keys() and _MATERIALS[path]:
            self.compiler_error = _MATERIALS[path].compiler_error
            self.parameters.setup(_MATERIALS[path].parameters)
        else:
            self.compiler_error = ''
            self.parameters.setup({})
            track_shader_changes()
    
    def update_nodes(self, context):
        self.parameters.parent = self.shader_nodes
        self.update_source(context)
    
    def poll_tree(self, object):
        return object.bl_idname == 'MaltTree' and (object.graph_type == self.material_type or self.material_type == '')
    
    material_type : bpy.props.StringProperty(name='Type',
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    shader_source : bpy.props.StringProperty(name="Shader Source", subtype='FILE_PATH', update=update_source,
        set=malt_path_setter('shader_source'), get=malt_path_getter('shader_source'),
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
        
    shader_nodes : bpy.props.PointerProperty(name="Node Tree", type=bpy.types.NodeTree, update=update_nodes, poll=poll_tree,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    compiler_error : bpy.props.StringProperty(name="Compiler Error",
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    parameters : bpy.props.PointerProperty(type=MaltPropertyGroup, name="Shader Parameters",
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def get_source_path(self):
        path = None
        if self.shader_nodes:
            if self.shader_nodes.is_active():
                path = self.shader_nodes.get_generated_source_path()
        else:
            path = bpy.path.abspath(self.shader_source, library=self.id_data.library)
        if path:
            return path
        else:
            return ''
    
    def draw_ui(self, layout, extension, material_parameters):
        layout.active = self.id_data.library is None #only local data can be edited
        layout.prop_search(self, 'material_type', bpy.context.scene.world.malt, 'material_types')
        row = layout.row()
        row.active = self.shader_nodes is None
        row.prop(self, 'shader_source')

        def nodes_add_or_duplicate():
            if self.shader_nodes:
                copy = self.shader_nodes.copy()
                copy.reload_nodes()
                copy.update_ext(force_update=True)
                self.shader_nodes = copy
            else:
                self.shader_nodes = bpy.data.node_groups.new(f'{self.id_data.name} Node Tree', 'MaltTree')
                self.shader_nodes.graph_type = self.material_type
            self.id_data.update_tag()
            self.shader_nodes.update_tag()
        row = layout.row(align=True)
        row.template_ID(self, "shader_nodes")
        if self.shader_nodes:
            row.operator('wm.malt_callback', text='', icon='DUPLICATE').callback.set(nodes_add_or_duplicate, 'Duplicate')
            from BlenderMalt.MaltNodes.MaltNodeTree import set_node_tree
            row.operator('wm.malt_callback', text = '', icon = 'GREASEPENCIL').callback.set(
                lambda: set_node_tree(bpy.context, self.shader_nodes)
            )
        else:
            row.operator('wm.malt_callback', text='New', icon='ADD').callback.set(nodes_add_or_duplicate, 'New')

        source_path = self.get_source_path()

        if source_path != '' and source_path.endswith(extension) == False:
            box = layout.box()
            box.label(text='Wrong shader extension, should be '+extension+'.', icon='ERROR')
            return
            
        if self.compiler_error != '':
            layout.operator("wm.malt_print_error", icon='ERROR').message = self.compiler_error
            box = layout.box()
            lines = self.compiler_error.splitlines()
            for line in lines:
                box.label(text=line)
        
        material_parameters.draw_ui(layout, filter=extension)
        self.parameters.draw_ui(layout)


class MALT_PT_MaterialSettings(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    bl_context = "material"
    bl_label = "Malt Settings"
    COMPAT_ENGINES = {'MALT'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT' and context.object is not None

    def draw(self, context):
        layout = self.layout
        ob = context.object
        slot = context.material_slot

        if ob:
            is_sortable = len(ob.material_slots) > 1
            rows = 3
            if is_sortable:
                rows = 5

            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ADD', text="")
            col.operator("object.material_slot_remove", icon='REMOVE', text="")

            col.separator()

            col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()

                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        row = layout.row(align=True)

        if ob:
            row.template_ID(ob, "active_material")
            def add_or_duplicate():
                nonlocal ob, slot
                name = f'{ob.data.name} Material'
                material = None
                if slot and slot.material:
                    material = slot.material.copy()
                else:
                    material = bpy.data.materials.new(name)
                material.malt.material_type = 'Mesh'
                if slot:
                    slot.material = material
                else:
                    ob.data.materials.append(material)
                ob.data.update_tag()
                material.update_tag()
            
            if slot and slot.material:
                row.operator('wm.malt_callback', text='', icon='DUPLICATE').callback.set(
                    add_or_duplicate, 'Duplicate')
            else:
                row.operator('wm.malt_callback', text='New', icon='ADD').callback.set(
                    add_or_duplicate, 'New')
            if slot:
                icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
                row.prop(slot, "link", icon=icon_link, icon_only=True)

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")
        
        if context.material:
            context.material.malt.draw_ui(layout, '.mesh.glsl', context.material.malt_parameters)


classes = (
    MaltMaterial,
    MALT_PT_MaterialSettings
)

def reset_materials():
    global _MATERIALS
    _MATERIALS = {}

import time
__TIMESTAMP = time.time()

INITIALIZED = False
def track_shader_changes(force_update=False, async_compilation=True):
    from BlenderMalt import MaltPipeline
    if MaltPipeline.is_malt_active() == False and force_update == False:
        return 1
        
    global INITIALIZED
    global __TIMESTAMP
    global _MATERIALS
    try:
        start_time = time.time()

        needs_update = []

        for material in bpy.data.materials:
            path = material.malt.get_source_path()
            if path not in needs_update:
                if os.path.exists(path):
                    stats = os.stat(path)
                    if path not in _MATERIALS.keys() or stats.st_mtime > __TIMESTAMP:
                        if path not in _MATERIALS:
                            _MATERIALS[path] = None
                        needs_update.append(path)

        compiled_materials = {}

        from . import MaltPipeline
        if len(needs_update) > 0:
            compiled_materials = MaltPipeline.get_bridge().compile_materials(needs_update, async_compilation=async_compilation)
        else:
            compiled_materials = MaltPipeline.get_bridge().receive_async_compilation_materials()
        
        if len(compiled_materials) > 0:
            for key, value in compiled_materials.items():
                _MATERIALS[key] = value
            for material in bpy.data.materials:
                path = material.malt.get_source_path()
                if path in compiled_materials.keys():
                    material.malt.compiler_error = compiled_materials[path].compiler_error
                    #TODO: Use parent parameters as defaults for materials with nodes
                    material.malt.parameters.setup(compiled_materials[path].parameters)
            for screen in bpy.data.screens:
                for area in screen.areas:
                    area.tag_redraw()
        
        __TIMESTAMP = start_time
        INITIALIZED = True
    except:
        import traceback
        traceback.print_exc()
    return 0.1 #Track again in 0.1 second
    

def register():
    for _class in classes: bpy.utils.register_class(_class)
    bpy.types.Material.malt = bpy.props.PointerProperty(type=MaltMaterial,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    bpy.app.timers.register(track_shader_changes, persistent=True)

def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)
    del bpy.types.Material.malt
    
    bpy.app.timers.unregister(track_shader_changes)
