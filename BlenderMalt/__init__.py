# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

bl_info = {
    "name": "BlenderMalt",
    "author" : "Miguel Pozo",
    "description" : "Extensible Python Render Engine",
    "blender" : (2, 80, 0),
    "category": "Render"
}

import bpy
import sys
from os import path

#Add Malt and dependencies to the import path
current_dir = path.dirname(path.realpath(__file__))
malt_path = path.join(current_dir, 'MaltPath')
malt_dependencies_path = path.join(current_dir, 'MaltDependencies')
if malt_path not in sys.path: sys.path.append(malt_path)
if malt_dependencies_path not in sys.path: sys.path.append(malt_dependencies_path)

#ENSURE DEPENDENCIES ARE INSTALLED
try:
    import OpenGL, OpenGL_accelerate, pcpp, pyrr
except:
    import subprocess, site
    def install_dependencies():
        dependencies = ['PyOpenGL', 'PyOpenGL_accelerate', 'pcpp', 'Pyrr']
        subprocess.check_call([bpy.app.binary_path_python, '-m', 'pip', 'install', *dependencies, '--target', malt_dependencies_path])
    try:
        install_dependencies()
    except:
        import os, ensurepip
        ensurepip.bootstrap()
        os.environ.pop("PIP_REQ_TRACKER", None) #https://developer.blender.org/T71856 :(
        install_dependencies()

import Malt

from BlenderMalt import MaltLights
from BlenderMalt import MaltMaterial
from BlenderMalt import MaltProperties
from BlenderMalt import MaltMeshes
from BlenderMalt import MaltPipeline
from BlenderMalt import MaltRenderEngine

modules = [
    MaltProperties,#MaltProperties must register before MaltMaterial
    MaltLights,
    MaltMaterial,
    MaltMeshes,
    MaltPipeline,
    MaltRenderEngine,
]

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

    malt_library_path : bpy.props.StringProperty(name="Malt Library Path", subtype='DIR_PATH')

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "malt_library_path")


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
