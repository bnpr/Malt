# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import os

import bpy

from Malt.Shader import Shader
from BlenderMalt import MaltProperties
from BlenderMalt.MaltProperties import MaltPropertyGroup
from BlenderMalt import MaltPipeline

#ShaderPath/PipelineName/PassName
SHADERS = {}

class MaltMaterial(bpy.types.PropertyGroup):

    def update_source(self, context):
        #TODO: Store source locally (for linked data and deleted files)
        global SHADERS
        self.compiler_error = ''
        uniforms = {}

        if self.shader_source != '':
            path = bpy.path.abspath(self.shader_source)
            if os.path.exists(path):
                pipeline_material = {}
                SHADERS[self.shader_source] = pipeline_material

                pipelines = [MaltPipeline.get_pipeline()]#TODO: get all active pipelines
                for pipeline in pipelines:
                    pipeline_name = pipeline.__class__.__name__
                    pipeline_material[pipeline_name] = pipeline.compile_material(path)

                    for pass_name, shader in pipeline_material[pipeline_name].items():
                        for uniform_name, uniform in shader.uniforms.items():
                            uniforms[uniform_name] = uniform
                        if shader.error:
                            self.compiler_error += pipeline_name + " : " + pass_name + " : " + shader.error
                        if shader.validator:
                            self.compiler_error += pipeline_name + " : " + pass_name + " : " + shader.validator
            else:
                self.compiler_error = 'Invalid file path'

        self.parameters.setup(uniforms)
    
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

                for name, parameter in self.parameters.items():
                    if name in pass_shader_copy.uniforms.keys():
                        pass_shader_copy.uniforms[name].set_value(parameter)
                    
                    if name in pass_shader_copy.textures.keys():
                        pass_shader_copy.textures[name] = MaltProperties.get_color_ramp_texture(self.id_data, name)
                
                for name, parameter in self.parameters.bools.items():
                    if name in pass_shader_copy.uniforms.keys():
                        pass_shader_copy.uniforms[name].set_value(parameter.boolean)

                for name, texture in self.parameters.textures.items():
                    if texture.texture and name in pass_shader_copy.textures.keys():
                        texture.texture.gl_load()
                        pass_shader_copy.textures[name] = texture.texture.bindcode

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
        material = None
        #Use always slot 0 since we don't support multi-material objects yet
        if ob and len(ob.material_slots) > 0:
            slot = ob.material_slots[0]
            material = slot.material
            row = layout.row()
            row.template_ID(slot, "material", new="material.new")
            icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
            row.prop(slot, "link", icon=icon_link, icon_only=True)
        else:
            layout.operator("object.material_slot_add", icon='ADD')

        layout.separator()
        layout.label(text="Material Settings:")
        
        if material:
            material.malt.draw_ui(layout)


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
