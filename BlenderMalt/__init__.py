# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

bl_info = {
    "name": "BlenderMalt",
    "author" : "Miguel Pozo",
    "description" : "Extensible Python Render Engine",
    "blender" : (2, 80, 0),
    "category": "Render"
}

import sys, os
from os import path
import bpy

#Add Malt and dependencies to the import path
__CURRENT_DIR = path.dirname(path.realpath(__file__))
__MALT_PATH = path.join(__CURRENT_DIR, '.MaltPath')
if __MALT_PATH not in sys.path: sys.path.append(__MALT_PATH)
_PY_VERSION = str(sys.version_info[0])+str(sys.version_info[1])
__MALT_DEPENDENCIES_PATH = path.join(__MALT_PATH,'Malt','.Dependencies-{}'.format(_PY_VERSION))
if __MALT_DEPENDENCIES_PATH not in sys.path: sys.path.append(__MALT_DEPENDENCIES_PATH)

from BlenderMalt.MaltUtils import malt_path_getter, malt_path_setter

class Preferences(bpy.types.AddonPreferences):
    # this must match the addon name
    bl_idname = __package__

    setup_vs_code : bpy.props.BoolProperty(name="Auto setup VSCode", default=True, description="Setups a VSCode project on your .blend file folder")

    renderdoc_path : bpy.props.StringProperty(name="RenderDoc Path", subtype='FILE_PATH',
        set=malt_path_setter('renderdoc_path'), get=malt_path_getter('renderdoc_path'))
    
    malt_library_path : bpy.props.StringProperty(name="Malt Library Path", subtype='DIR_PATH')
    
    render_fps_cap : bpy.props.IntProperty(name="Max Viewport Render Framerate", default=30)
    
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
        layout.prop(self, "renderdoc_path")
        layout.prop(self, "malt_library_path")
        layout.prop(self, "render_fps_cap")
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
    "python.analysis.extraPaths": ["{}","{}"],
}}
'''

@bpy.app.handlers.persistent
def setup_vs_code(dummy):
    if bpy.context.scene.render.engine == 'MALT':
        if bpy.context.preferences.addons['BlenderMalt'].preferences.setup_vs_code:
            shaders_path = path.join(__MALT_PATH, 'Malt', 'Shaders')
            intellisense_path = path.join(shaders_path, 'Intellisense', 'intellisense.glsl')
            library_path = bpy.context.preferences.addons['BlenderMalt'].preferences.malt_library_path

            vscode_settings = _VS_CODE_SETTINGS.format(shaders_path, library_path, intellisense_path, __MALT_PATH, __MALT_DEPENDENCIES_PATH)
            vscode_settings = vscode_settings.replace('\\','\\\\')

            settings_dir = bpy.path.abspath('//.vscode')

            if path.exists(settings_dir) == False:
                os.makedirs(settings_dir)

            with open(path.join(settings_dir, 'settings.json'), 'w') as f:
                f.write(vscode_settings)

def do_windows_fixes():
    import platform, multiprocessing as mp, ctypes
    from shutil import copy
    # Workaround https://developer.blender.org/rB04c5471ceefb41c9e49bf7c86f07e9e7b8426bb3
    if platform.system() == 'Windows':
        sys.executable = sys._base_executable
        # Use python-gpu on windows (patched python with NvOptimusEnablement and AmdPowerXpressRequestHighPerformance)
        python_executable = path.join(sys.exec_prefix, 'bin', 'python-gpu-{}.exe'.format(_PY_VERSION))
        if os.path.exists(python_executable) == False:
            python_gpu_path = path.join(__MALT_DEPENDENCIES_PATH, 'python-gpu-{}.exe'.format(_PY_VERSION))
            try:
                copy(python_gpu_path, python_executable)
            except PermissionError as e:
                command = '/c copy "{}" "{}"'.format(python_gpu_path, python_executable)
                result = ctypes.windll.shell32.ShellExecuteW(None, 'runas', 'cmd.exe', command, None, 0)
        mp.set_executable(python_executable)

def get_modules():
    from . import MaltUtils, MaltTextures, MaltMeshes, MaltLights, MaltProperties, MaltPipeline, MaltMaterial, MaltRenderEngine
    from . MaltNodes import _init_ as MaltNodes
    return [ MaltUtils, MaltTextures, MaltMeshes, MaltLights, MaltProperties, MaltPipeline, MaltNodes, MaltMaterial, MaltRenderEngine ]

classes=[
    Preferences,
]

def register():
    import importlib
    for module in get_modules():
        importlib.reload(module)
    
    import Bridge
    Bridge.reload()

    do_windows_fixes()

    for _class in classes: bpy.utils.register_class(_class)

    for module in get_modules():
        module.register()

    bpy.app.handlers.save_post.append(setup_vs_code)

def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

    for module in reversed(get_modules()):
        module.unregister()
    
    bpy.app.handlers.save_post.remove(setup_vs_code)
