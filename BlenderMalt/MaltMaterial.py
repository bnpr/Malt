# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import os

import bpy

from BlenderMalt.MaltProperties import MaltPropertyGroup
from BlenderMalt import MaltPipeline

_SHADER_PATHS = []
class MaltMaterial(bpy.types.PropertyGroup):

    def update_source(self, context):
        #print('UPDATE SOURCE')
        global _SHADER_PATHS
        if str(self.shader_source) not in _SHADER_PATHS:
            _SHADER_PATHS.append(str(self.shader_source))
        self.compiler_error = ''
        if self.shader_source != '':
            path = bpy.path.abspath(self.shader_source)
            compiled_material = MaltPipeline.get_bridge().compile_material(path)
            self.compiler_error = compiled_material.compiler_error
            self.parameters.setup(compiled_material.parameters)
        else:
            self.parameters.setup({})
        
    shader_source : bpy.props.StringProperty(name="Shader Source", subtype='FILE_PATH', update=update_source)
    compiler_error : bpy.props.StringProperty(name="Compiler Error")

    parameters : bpy.props.PointerProperty(type=MaltPropertyGroup, name="Shader Parameters")
    
    def draw_ui(self, layout, extension):
        layout.prop(self, 'shader_source')
        if self.shader_source != '' and self.shader_source.endswith('.'+extension+'.glsl') == False:
            box = layout.box()
            box.label(text='Wrong shader extension, should be '+extension+'.', icon='ERROR')
            return
            
        if self.compiler_error != '':
            layout.operator("wm.malt_print_error", icon='ERROR').message = self.compiler_error
            #layout.label(text='COMPILER ERROR:', icon='ERROR')
            box = layout.box()
            lines = self.compiler_error.splitlines()
            for line in lines:
                box.label(text=line)
        self.parameters.draw_ui(layout)


class MALT_PT_MaterialSettings(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    bl_context = "material"
    bl_label = "Material Settings"
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

        row = layout.row()

        if ob:
            row.template_ID(ob, "active_material", new="material.new")

            if slot:
                icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
                row.prop(slot, "link", icon=icon_link, icon_only=True)

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")
        
        if context.material:
            context.material.malt.draw_ui(layout, 'mesh')#TODO


classes = (
    MaltMaterial,
    MALT_PT_MaterialSettings
)

def reset_materials():
    global _SHADER_PATHS
    _SHADER_PATHS = []

import time
import traceback
__TIMESTAMP = time.time()

INITIALIZED = False
def track_shader_changes():
    if bpy.context.scene.render.engine != 'MALT':
        return 1
        
    global INITIALIZED
    global __TIMESTAMP
    global _SHADER_PATHS
    try:
        start_time = time.time()

        #print('TRACK UPDATES')

        needs_update = []

        for material in bpy.data.materials:
            path = bpy.path.abspath(material.malt.shader_source)
            if path not in needs_update:
                if os.path.exists(path):
                    stats = os.stat(path)
                    if path not in _SHADER_PATHS or stats.st_mtime > __TIMESTAMP:
                        if path not in _SHADER_PATHS:
                            _SHADER_PATHS.append(path)
                        needs_update.append(path)
        
        #print(needs_update)

        if len(needs_update) > 0:
            compiled_materials = MaltPipeline.get_bridge().compile_materials(needs_update)
            for material in bpy.data.materials:
                path = bpy.path.abspath(material.malt.shader_source)
                if path in compiled_materials.keys():
                    material.malt.compiler_error = compiled_materials[path].compiler_error
                    material.malt.parameters.setup(compiled_materials[path].parameters)
            for screen in bpy.data.screens:
                for area in screen.areas:
                    area.tag_redraw()
        
        __TIMESTAMP = start_time
        INITIALIZED = True
    except:
        traceback.print_exc()
        pass
    return 1 #Track again in 1 second
    

def register():
    for _class in classes: bpy.utils.register_class(_class)
    bpy.types.Material.malt = bpy.props.PointerProperty(type=MaltMaterial)
    
    bpy.app.timers.register(track_shader_changes, persistent=True)

def unregister():
    for _class in classes: bpy.utils.unregister_class(_class)
    del bpy.types.Material.malt
    
    bpy.app.timers.unregister(track_shader_changes)
