# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy

from .Properties import MaltPropertyGroup
from . import MaltPipeline

import os

class MaltMaterial(bpy.types.PropertyGroup):

    def update_source(self, context):
        self.compiler_error = ''
        if self.shader_source != '':
            if os.path.exists(self.shader_source):
                compile_result = MaltPipeline.get_pipeline().compile_shader(self.shader_source)
                self.parameters.setup(compile_result['uniforms'])
                if compile_result['error']:
                    self.compiler_error = compile_result['error']
            else:
                self.compiler_error = 'Invalid file path'
        
    shader_source : bpy.props.StringProperty(name="Shader Source", subtype='FILE_PATH', update=update_source)
    compiler_error : bpy.props.StringProperty(name="Compiler Error")

    parameters : bpy.props.PointerProperty(type=MaltPropertyGroup, name="Parameters")
    
    def draw_ui(self, layout):
        layout.prop(self, 'shader_source')
        if self.compiler_error != '':
            layout.label(text='COMPILER ERROR:', icon='ERROR')
            box = layout.box()
            lines = self.compiler_error.splitlines()
            for line in lines:
                box.label(text=line)
        self.parameters.draw_ui(layout)


class MaltMaterialPanel(bpy.types.Panel):
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
        material = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data

        if ob:
            layout.template_ID(ob, "active_material", new="material.new")
            row = layout.row()

            if slot:
                row.prop(slot, "link", text="")
            else:
                row.label()
        elif material:
            layout.template_ID(space, "pin_id")
            layout.separator()

        layout.separator()
        layout.label(text="Material Settings:")
        
        if material:
            material.malt.draw_ui(layout)


classes = (
    MaltMaterial,
    MaltMaterialPanel
)

import time
__TIMESTAMP = time.time()

def watch_for_changes():
    global __TIMESTAMP
    start_time = time.time()

    for material in bpy.data.materials:
        if os.path.exists(material.malt.shader_source):
            stats = os.stat(material.malt.shader_source)
            if stats.st_mtime > __TIMESTAMP:
                material.malt.update_source(bpy.context)

    __TIMESTAMP = start_time

    return 1

def register():
    for _class in classes: bpy.utils.register_class(_class)
    bpy.types.Material.malt = bpy.props.PointerProperty(type=MaltMaterial)

    bpy.app.timers.register(watch_for_changes, persistent=True)

def unregister():
    for _class in classes: bpy.utils.unregister_class(_class)
    del bpy.types.Material.malt
    
    bpy.app.timers.unregister(watch_for_changes)
