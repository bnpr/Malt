bl_info = {
    "name": "BlenderMalt",
    "description" : "Extensible Python Render Engine",
    "author" : "Miguel Pozo",
    "version": (1,0,0,'beta.2','Development'),
    "blender" : (3, 2, 0),
    "doc_url": "https://malt3d.com",
    "tracker_url": "https://github.com/bnpr/Malt/issues/new/choose",
    "category": "Render"
}

import sys, os
from os import path
import bpy

def version_missmatch():
    return bpy.app.version[:2] != bl_info['blender'][:2]
def version_missmatch_message():
    if version_missmatch():
        v = bl_info['blender']
        return f"Malt loading aborted. The installed Malt version only works with Blender {v[0]}.{v[1]}"

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

    setup_vs_code : bpy.props.BoolProperty(name="Auto setup VSCode", default=True,
        description="Setups a VSCode project on your .blend file folder")

    renderdoc_path : bpy.props.StringProperty(name="RenderDoc Path", subtype='FILE_PATH',
        set=malt_path_setter('renderdoc_path'), get=malt_path_getter('renderdoc_path'))
    
    plugins_dir : bpy.props.StringProperty(name="Global Plugins", subtype='DIR_PATH',
        set=malt_path_setter('plugins_dir'), get=malt_path_getter('plugins_dir'))
    
    docs_path : bpy.props.StringProperty(name="Docs Path", subtype='DIR_PATH',
        set=malt_path_setter('docs_path'), get=malt_path_getter('docs_path'))
    
    render_fps_cap : bpy.props.IntProperty(name="Max Viewport Render Framerate", default=30)
    
    def update_debug_mode(self, context):
        if context.scene.render.engine == 'MALT':
            context.scene.world.malt.update_pipeline(context)

    debug_mode : bpy.props.BoolProperty(name="Debug Mode", default=False, update=update_debug_mode,
        description="Developers only. Do not touch !!!")

    #Drawn in NODE_PT_overlay
    show_socket_types : bpy.props.BoolProperty(name='Show Socket Types', default=True)
    show_internal_nodes : bpy.props.BoolProperty(name='Show Internal Nodes', default=False)

    def draw(self, context):
        layout = self.layout

        if version_missmatch():
            layout.label(text=version_missmatch_message(), icon='ERROR')
            return
        
        if context.scene.render.engine == 'MALT':
            layout.operator('wm.path_open', text="Open Session Log").filepath=sys.stdout.log_path
        else:
            row = layout.row()
            row.enabled = False
            row.operator('wm.path_open', text="Open Session Log")

        layout.prop(self, "plugins_dir")
        layout.prop(self, "render_fps_cap")
        layout.prop(self, "setup_vs_code")
        layout.prop(self, "renderdoc_path")
        layout.label(text='Developer Settings :')
        layout.prop(self, "debug_mode")
        layout.prop(self, "docs_path")
    
def draw_node_tree_overlays(self:bpy.types.Menu, context: bpy.types.Context):
    preferences = bpy.context.preferences.addons['BlenderMalt'].preferences
    self.layout.label(text='Malt')
    self.layout.prop(preferences, 'show_socket_types')
    self.layout.prop(preferences, 'show_internal_nodes')

_VS_CODE_SETTINGS = '''
{{
    "files.associations": {{
        "*.glsl": "cpp"
    }},
    "C_Cpp.default.includePath": ["{}"],
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

            vscode_settings = _VS_CODE_SETTINGS.format(shaders_path, intellisense_path, __MALT_PATH, __MALT_DEPENDENCIES_PATH)
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

_PLUGINS = []
_PLUGIN_DIRS = []

def register_plugins():
    global _PLUGINS, _PLUGIN_DIRS
    preferences = bpy.context.preferences.addons['BlenderMalt'].preferences
    plugins_dir = preferences.plugins_dir
    if not os.path.exists(plugins_dir):
        return
    import importlib
    if plugins_dir not in sys.path:
        sys.path.append(plugins_dir)
        _PLUGIN_DIRS.append(plugins_dir)
    for e in os.scandir(plugins_dir):
        if (e.path.startswith('.') or e.path.startswith('_') or 
            e.is_file() and e.path.endswith('.py') == False):
            continue
        try:
            module = importlib.import_module(e.name)
            importlib.reload(module)
            module.PLUGIN.blendermalt_register()
            _PLUGINS.append(module.PLUGIN)
        except:
            import traceback
            traceback.print_exc()

def unregister_plugins():
    global _PLUGINS, _PLUGIN_DIRS
    for plugin in _PLUGINS:
        try:
            plugin.blendermalt_unregister()
        except:
            import traceback
            traceback.print_exc()
    _PLUGINS = []
    for dir in _PLUGIN_DIRS:
        sys.path.remove(dir)
    _PLUGIN_DIRS = []

class OT_MaltReloadPlugins(bpy.types.Operator):
    bl_idname = "wm.malt_reload_plugins"
    bl_label = "Malt Reload Plugins"

    def execute(self, context):
        unregister_plugins()
        bpy.ops.wm.malt_reload_pipeline()
        register_plugins()
        return{"FINISHED"}

def get_modules():
    from . import MaltUtils, MaltTextures, MaltMeshes, MaltLights, MaltProperties, MaltPipeline, MaltMaterial, MaltRenderEngine
    from . MaltNodes import _init_ as MaltNodes
    return [ MaltUtils, MaltTextures, MaltMeshes, MaltLights, MaltProperties, MaltPipeline, MaltNodes, MaltMaterial, MaltRenderEngine ]

classes=[
    Preferences,
    OT_MaltReloadPlugins,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
    if version_missmatch():
        print(version_missmatch_message())
        return

    import importlib
    for module in get_modules():
        importlib.reload(module)
    
    import Bridge
    Bridge.reload()

    do_windows_fixes()

    for module in get_modules():
        module.register()

    register_plugins()

    bpy.app.handlers.save_post.append(setup_vs_code)

    bpy.types.NODE_PT_overlay.append(draw_node_tree_overlays)

def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)
    
    if version_missmatch():
        return

    unregister_plugins()

    for module in reversed(get_modules()):
        module.unregister()
    
    bpy.app.handlers.save_post.remove(setup_vs_code)

    bpy.types.NODE_PT_overlay.remove(draw_node_tree_overlays)
