# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

bl_info = {
    "name": "BlenderMalt",
    "author" : "Miguel Pozo",
    "description" : "Extensible Python Render Engine",
    "blender" : (2, 80, 0),
    "category": "Render"
}

import bpy, sys, os
from os import path

#Add Malt and dependencies to the import path
current_dir = path.dirname(path.realpath(__file__))
malt_path = path.join(current_dir, '.MaltPath')
if malt_path not in sys.path: sys.path.append(malt_path)
malt_dependencies_path = path.join(malt_path,'Malt','.Dependencies')
if malt_dependencies_path not in sys.path: sys.path.append(malt_dependencies_path)

import Malt
import Bridge

from BlenderMalt import MaltLights
from BlenderMalt import MaltMaterial
from BlenderMalt import MaltProperties
from BlenderMalt import MaltMeshes
from BlenderMalt import MaltPipeline
from BlenderMalt import MaltRenderEngine
from BlenderMalt import MaltTextures

modules = [
    MaltPipeline,
    MaltProperties,#MaltProperties must register before MaltMaterial
    MaltTextures,
    MaltMeshes,
    MaltMaterial,
    MaltLights,
    MaltRenderEngine,
]

if "bpy" in locals():
    #TODO: Module dependency order is important for reloading
    # Maybe reload twice ?
    import importlib
    for module in Malt.modules:
        importlib.reload(module)
    for module in Bridge.modules:
        importlib.reload(module)
    for module in modules:
        importlib.reload(module)


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


class Preferences(bpy.types.AddonPreferences):
    # this must match the addon name
    bl_idname = __package__

    malt_library_path : bpy.props.StringProperty(name="Malt Library Path", subtype='DIR_PATH')
    
    setup_vs_code : bpy.props.BoolProperty(name="Auto setup VSCode", default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "malt_library_path")
        layout.prop(self, "setup_vs_code")


_VS_CODE_SETTINGS = '''
{{
    "files.associations": {{
        "*.glsl": "cpp"
    }},
    "C_Cpp.default.includePath": ["{}","{}"],
    "C_Cpp.default.forcedInclude": ["{}"],
    "C_Cpp.autoAddFileAssociations": true,
    "C_Cpp.default.cppStandard": "c++03",
    "C_Cpp.default.compilerPath": "",
    "C_Cpp.default.browse.limitSymbolsToIncludedHeaders": true,
    "C_Cpp.errorSquiggles": "Disabled",
}}
'''

@bpy.app.handlers.persistent
def setup_vs_code(dummy):
    if bpy.context.scene.render.engine == 'MALT':
        if bpy.context.preferences.addons['BlenderMalt'].preferences.setup_vs_code:
            source_path = path.dirname(__file__)
            shaders_path = path.join(source_path, 'MaltPath', 'Malt', 'Shaders')
            intellisense_path = path.join(shaders_path, 'Intellisense', 'intellisense.glsl')
            library_path = bpy.context.preferences.addons['BlenderMalt'].preferences.malt_library_path

            vscode_settings = _VS_CODE_SETTINGS.format(shaders_path, library_path, intellisense_path)
            vscode_settings = vscode_settings.replace('\\','\\\\')

            settings_dir = bpy.path.abspath('//.vscode')

            if path.exists(settings_dir) == False:
                os.makedirs(settings_dir)

            with open(path.join(settings_dir, 'settings.json'), 'w') as f:
                f.write(vscode_settings)

classes=[
    Preferences,
    OT_MaltPrintError,
]

import multiprocessing as mp

def register():
    for _class in classes: bpy.utils.register_class(_class)

    for module in modules:
        module.register()

    bpy.app.handlers.save_post.append(setup_vs_code)

def unregister():
    for _class in classes: bpy.utils.unregister_class(_class)

    for module in modules:
        module.unregister()
    
    bpy.app.handlers.save_post.remove(setup_vs_code)


if __name__ == "__main__":
    register()
