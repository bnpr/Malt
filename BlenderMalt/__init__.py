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

    setup_vs_code : bpy.props.BoolProperty(name="Auto setup VSCode", default=True, description="Setups a VSCode project on your .blend file folder")
    
    malt_library_path : bpy.props.StringProperty(name="Malt Library Path", subtype='DIR_PATH')
    
    def update_debug_mode(self, context):
        if context.scene.render.engine == 'MALT':
            context.scene.world.malt.update_pipeline(context)

    debug_mode : bpy.props.BoolProperty(name="Debug Mode", default=False, update=update_debug_mode, description="Developers only. Do not touch !!!")

    def draw(self, context):
        layout = self.layout
        
        if context.scene.render.engine == 'MALT':
            layout.operator('wm.path_open', text="Open Session Log").filepath=sys.stdout.log_path
        else:
            row = layout.row()
            row.enabled = False
            row.operator('wm.path_open', text="Open Session Log")

        layout.prop(self, "setup_vs_code")
        layout.prop(self, "malt_library_path")
        layout.prop(self, "debug_mode")


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
            shaders_path = path.join(malt_path, 'Malt', 'Shaders')
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

def register():
    import platform, multiprocessing as mp, ctypes
    from shutil import copy
    # Workaround https://developer.blender.org/rB04c5471ceefb41c9e49bf7c86f07e9e7b8426bb3
    if platform.system() == 'Windows':
        sys.executable = sys._base_executable
        # Use python-gpu on windows (patched python with NvOptimusEnablement and AmdPowerXpressRequestHighPerformance)
        python_executable = path.join(sys.exec_prefix, 'bin', 'python-gpu.exe')
        if os.path.exists(python_executable) == False:
            python_gpu_path = path.join(malt_dependencies_path, 'python-gpu.exe')
            try:
                copy(python_gpu_path, python_executable)
            except PermissionError as e:
                command = '/c copy "{}" "{}"'.format(python_gpu_path, python_executable)
                result = ctypes.windll.shell32.ShellExecuteW(None, 'runas', 'cmd.exe', command, None, 0)
        mp.set_executable(python_executable)

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
