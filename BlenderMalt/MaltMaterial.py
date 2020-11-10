# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import os

import bpy

from Malt.Parameter import *
from Malt.Shader import Shader
from Malt.Pipeline import Pipeline
from BlenderMalt import MaltProperties
from BlenderMalt.MaltProperties import MaltPropertyGroup
from BlenderMalt import MaltPipeline

#ShaderPath/PipelineName/PassName
SHADERS = {}

def find_shader_path(path):
    full_path = bpy.path.abspath(path)
    if os.path.exists(full_path):
        return full_path
    for shader_path in Pipeline.SHADER_INCLUDE_PATHS:
        full_path = os.path.join(shader_path, path)
        if os.path.exists(full_path):
            return full_path
    return None

class MaltMaterial(bpy.types.PropertyGroup):

    def update_source(self, context):
        #TODO: Store source locally (for linked data and deleted files)
        global SHADERS
        self.compiler_error = ''
        parameters = {}

        if self.shader_source != '':
            path = find_shader_path(self.shader_source)
            if path:
                pipeline_material = {}
                SHADERS[self.shader_source] = pipeline_material

                pipelines = [MaltPipeline.get_pipeline()]#TODO: get all active pipelines
                for pipeline in pipelines:
                    pipeline_name = pipeline.__class__.__name__
                    pipeline_material[pipeline_name] = pipeline.compile_material(path)

                    for pass_name, shader in pipeline_material[pipeline_name].items():
                        for uniform_name, uniform in shader.uniforms.items():
                            parameters[uniform_name] = Parameter.from_uniform(uniform)
                        if shader.error:
                            self.compiler_error += pipeline_name + " : " + pass_name + " : " + shader.error
                        if shader.validator:
                            self.compiler_error += pipeline_name + " : " + pass_name + " : " + shader.validator
            else:
                self.compiler_error = 'Invalid file path'

        self.parameters.setup(parameters)
    
    def get_shader(self):
        global SHADERS
        if self.shader_source not in SHADERS.keys():
            return None

        shader = SHADERS[self.shader_source]
        new_shader = {}

        for pipeline_name, pipeline in shader.items():
            new_shader[pipeline_name] = {}

            for pass_name, pass_shader in pipeline.items():
                if pass_shader.error:
                    new_shader[pipeline_name][pass_name] = None
                    continue

                pass_shader_copy = pass_shader.copy()
                new_shader[pipeline_name][pass_name] = pass_shader_copy

                for name, parameter in self.parameters.get_parameters().items():
                    if name in pass_shader_copy.textures.keys():
                        pass_shader_copy.textures[name] = parameter
                    elif name in pass_shader_copy.uniforms.keys():
                        pass_shader_copy.uniforms[name].set_value(parameter)

        return new_shader
        
    shader_source : bpy.props.StringProperty(name="Shader Source", subtype='FILE_PATH', update=update_source)
    compiler_error : bpy.props.StringProperty(name="Compiler Error")

    parameters : bpy.props.PointerProperty(type=MaltPropertyGroup, name="Shader Parameters")
    
    def draw_ui(self, layout):
        layout.prop(self, 'shader_source')
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
            context.material.malt.draw_ui(layout)


classes = (
    MaltMaterial,
    MALT_PT_MaterialSettings
)

import time
import traceback
__TIMESTAMP = time.time()

INITIALIZED = False
def track_shader_changes():
    global INITIALIZED
    global __TIMESTAMP
    global SHADERS
    try:
        redraw = False
        start_time = time.time()

        for material in bpy.data.materials:
            shader_path = material.malt.shader_source
            abs_path = bpy.path.abspath(shader_path)
            if os.path.exists(abs_path):
                stats = os.stat(abs_path)
                if shader_path not in SHADERS.keys() or stats.st_mtime > __TIMESTAMP:
                    redraw = True
                    material.malt.update_source(bpy.context)
        
        __TIMESTAMP = start_time
        INITIALIZED = True

        if redraw:
            for screen in bpy.data.screens:
                for area in screen.areas:
                    area.tag_redraw()
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
