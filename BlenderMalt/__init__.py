# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

bl_info = {
    "name": "Malt",
    "author" : "Miguel Pozo",
    "description" : "Extensible Python Render Engine",
    "blender" : (2, 80, 0),
    "category": "Render"
}

import bpy

#ENSURE DEPENDENCIES ARE INSTALLED
try:
    import OpenGL, pcpp
except:
    import os, subprocess, ensurepip
    ensurepip.bootstrap()
    os.environ.pop("PIP_REQ_TRACKER", None) #https://developer.blender.org/T71856 :(
    dependencies = ['PyOpenGL','pcpp']
    for dependency in dependencies:
        subprocess.check_call([bpy.app.binary_path_python, '-m', 'pip', 'install', dependency])


from . import MaltMaterial
from . import MaltProperties
from . import MaltMeshes
from . import MaltPipeline
from . import MaltRenderEngine

modules = [
    MaltProperties,#MaltProperties must register before MaltMaterial
    MaltMaterial,
    MaltMeshes,
    MaltPipeline,
    MaltRenderEngine,
]

from . import Malt

if "bpy" in locals():
    #TODO: Module dependency order is important for reloading
    # Maybe reload twice ?
    import importlib
    for module in Malt.modules:
        importlib.reload(module)
    for module in modules:
        importlib.reload(module)


class Preferences(bpy.types.AddonPreferences):
    # this must match the addon name
    bl_idname = __package__

    shader_library_path : bpy.props.StringProperty(name="Shader Library Path", subtype='DIR_PATH')

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "shader_library_path")


class OT_MaltPrintError(bpy.types.Operator):
    bl_idname = "wm.malt_print_error"
    bl_label = "Print Malt Error"
    bl_description = "MALT ERROR"

    message : bpy.props.StringProperty(default="Malt Error", description='Error Message')

    @classmethod
    def description(cls, context, properties):
        return properties.message

    def execute(self, context):
        self.report({'ERROR'}, self.message)
        return {'FINISHED'}
    
    def modal(self, context, event):
        self.report({'ERROR'}, self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

classes=[
    Preferences,
    OT_MaltPrintError,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)

    for module in modules:
        module.register()

def unregister():
    for _class in classes: bpy.utils.unregister_class(_class)

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
