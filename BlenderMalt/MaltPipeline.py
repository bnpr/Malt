import os, platform, time
import bpy
from BlenderMalt.MaltUtils import malt_path_getter, malt_path_setter
from . import MaltMaterial, MaltMeshes, MaltTextures

_BRIDGE = None
_PIPELINE_PARAMETERS = None
_TIMESTAMP = time.time()

def is_malt_active():
    if bpy.context.scene.render.engine == 'MALT':
        return True
    for scene in bpy.data.scenes:
        if scene.render.engine == 'MALT':
            return True
    return False

def get_bridge(world=None, force_creation=False):
    global _BRIDGE
    bridge = _BRIDGE
    if (bridge and bridge.lost_connection) or (bridge is None and force_creation):
        _BRIDGE = None
        if is_malt_active() == False:
            return None
        if world is None:
            world = bpy.context.scene.world
        world.malt.update_pipeline(bpy.context)
    return _BRIDGE

def sync_pipeline_settings(default_world=None):
    for scene in bpy.data.scenes:
        if scene.render.engine == 'MALT' and scene.world is None:
            scene.world = bpy.data.worlds.new(f'{scene.name} World')
            setup_parameters([scene.world])
    if default_world is None:
        default_world = bpy.data.worlds[0]
    for world in bpy.data.worlds:
        if world.malt.pipeline != default_world.malt.pipeline:
            world.malt.pipeline = default_world.malt.pipeline
        if world.malt.plugins_dir != default_world.malt.plugins_dir:
            world.malt.plugins_dir = default_world.malt.plugins_dir
        if world.malt.viewport_bit_depth != default_world.malt.viewport_bit_depth:
            world.malt.viewport_bit_depth = default_world.malt.viewport_bit_depth

_ON_PIPELINE_SETTINGS_UPDATE = False

class MaltPipeline(bpy.types.PropertyGroup):

    def update_pipeline(self, context):
        global _TIMESTAMP
        _TIMESTAMP = time.time()
        
        #TODO: Sync all scenes. Only one active pipeline per Blender instance is supported atm.
        pipeline = self.pipeline
        if pipeline == '':
            current_dir = os.path.dirname(os.path.abspath(__file__))
            default_pipeline = os.path.join(current_dir,'.MaltPath','Malt','Pipelines','NPR_Pipeline','NPR_Pipeline.py')
            if platform.system() == 'Darwin':
                # The NPR Pipeline doesn't work on OpenGL implementations limited to 16 sampler uniforms
                default_pipeline = os.path.join(current_dir,'.MaltPath','Malt','Pipelines','MiniPipeline','MiniPipeline.py')
            pipeline = default_pipeline
        
        preferences = bpy.context.preferences.addons['BlenderMalt'].preferences

        debug_mode = bool(preferences.debug_mode)
        renderdoc_path = preferences.renderdoc_path
        plugin_dirs = []
        if os.path.exists(preferences.plugins_dir):
            plugin_dirs.append(preferences.plugins_dir)
        plugin_dir = bpy.path.abspath(self.plugins_dir, library=self.id_data.library)
        if os.path.exists(plugin_dir):
            plugin_dirs.append(plugin_dir)
        
        docs_path = preferences.docs_path
        docs_path = docs_path if os.path.exists(docs_path) else None
        
        path = bpy.path.abspath(pipeline, library=self.id_data.library)
        import Bridge
        bridge = Bridge.Client_API.Bridge(path, int(self.viewport_bit_depth), debug_mode, renderdoc_path, plugin_dirs, docs_path)
        from Malt.Utils import LOG
        LOG.info('Blender {} {} {}'.format(bpy.app.version_string, bpy.app.build_branch, bpy.app.build_hash))
        params = bridge.get_parameters()

        global _BRIDGE, _PIPELINE_PARAMETERS
        _BRIDGE = bridge
        _PIPELINE_PARAMETERS = params
        
        MaltMaterial.reset_materials()
        MaltMeshes.reset_meshes()
        MaltTextures.reset_textures()
        
        #TODO: This can fail depending on the current context, ID classes might not be writeable
        setup_all_ids()

    def update_pipeline_settings(self, context):
        global _ON_PIPELINE_SETTINGS_UPDATE
        if _ON_PIPELINE_SETTINGS_UPDATE:
            return
        _ON_PIPELINE_SETTINGS_UPDATE = True

        sync_pipeline_settings(self.id_data)
        
        _ON_PIPELINE_SETTINGS_UPDATE = False
        
        self.update_pipeline(context)

    pipeline : bpy.props.StringProperty(name="Malt Pipeline", subtype='FILE_PATH', update=update_pipeline_settings,
        set=malt_path_setter('pipeline'), get=malt_path_getter('pipeline'),
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    plugins_dir : bpy.props.StringProperty(name="Local Plugins", subtype='DIR_PATH', update=update_pipeline_settings,
        set=malt_path_setter('plugins_dir'), get=malt_path_getter('plugins_dir'),
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    viewport_bit_depth : bpy.props.EnumProperty(items=[('8', '8', ''),('16', '16', ''),('32', '32', '')], 
        name="Bit Depth (Viewport)", update=update_pipeline_settings,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    graph_types : bpy.props.CollectionProperty(type=bpy.types.PropertyGroup,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'})
    material_types : bpy.props.CollectionProperty(type=bpy.types.PropertyGroup,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'})
    overrides : bpy.props.StringProperty(name='Pipeline Overrides', default='Preview,Final Render',
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def draw_ui(self, layout):
        layout.use_property_split = True
        layout.use_property_decorate = False
        row = layout.row(align=True)
        row.prop(self, 'pipeline')
        row.operator('wm.malt_reload_pipeline', text='', icon='FILE_REFRESH')
        layout.prop(self, 'plugins_dir')
        layout.prop(self, 'viewport_bit_depth')


class OT_MaltReloadPipeline(bpy.types.Operator):
    bl_idname = "wm.malt_reload_pipeline"
    bl_label = "Malt Reload Pipeline"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT' and context.scene.world is not None

    def execute(self, context):
        import Bridge
        Bridge.reload()
        context.scene.world.malt.update_pipeline(context)
        return {'FINISHED'}


class MALT_PT_Pipeline(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    bl_context = "world"
    bl_label = "Pipeline Settings"
    COMPAT_ENGINES = {'MALT'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT' and context.scene.world is not None

    def draw(self, context):
        context.scene.world.malt.draw_ui(self.layout)

classes = (
    MaltPipeline,
    OT_MaltReloadPipeline,
    MALT_PT_Pipeline,
)

def setup_all_ids():
    setup_parameters(bpy.data.scenes)
    setup_parameters(bpy.data.worlds)
    setup_parameters(bpy.data.cameras)
    setup_parameters(bpy.data.objects)
    setup_parameters(bpy.data.materials)
    setup_parameters(bpy.data.meshes)
    setup_parameters(bpy.data.curves)
    setup_parameters(bpy.data.metaballs)
    setup_parameters(bpy.data.lights)
    from . MaltNodes.MaltNodeTree import setup_node_trees
    setup_node_trees()
    MaltMaterial.track_shader_changes(force_update=True)

def setup_parameters(ids):
    global _PIPELINE_PARAMETERS
    pipeline_parameters = _PIPELINE_PARAMETERS

    class_parameters_map = {
        bpy.types.Scene : pipeline_parameters.scene,
        bpy.types.World : pipeline_parameters.world,
        bpy.types.Camera : pipeline_parameters.camera,
        bpy.types.Object : pipeline_parameters.object,
        bpy.types.Material : pipeline_parameters.material,
        bpy.types.Mesh : pipeline_parameters.mesh,
        bpy.types.Curve : pipeline_parameters.mesh,
        bpy.types.MetaBall : pipeline_parameters.mesh,
        bpy.types.Light : pipeline_parameters.light,
    }

    for bid in ids:
        if isinstance(bid, bpy.types.World):
            bid.malt.graph_types.clear()
            bid.malt.material_types.clear()
            for graph in get_bridge().graphs.values():
                bid.malt.graph_types.add().name = graph.name
                if graph.language == 'GLSL':
                    bid.malt.material_types.add().name = graph.name
            from BlenderMalt.MaltNodes import MaltCustomPasses
            MaltCustomPasses.setup_default_passes(get_bridge().graphs, bid)
        if isinstance(bid, bpy.types.Material):
            #Patch material types
            if bid.malt.material_type == '':
                if bid.malt.shader_nodes:
                    bid.malt.material_type = bid.malt.shader_nodes.graph_type
                else:
                    bid.malt.material_type = 'Mesh'
        for cls, parameters in class_parameters_map.items():
            if isinstance(bid, cls):
                bid.malt_parameters.setup(parameters)

_ON_DEPSGRAPH_UPDATE = False

@bpy.app.handlers.persistent
def depsgraph_update(scene, depsgraph):
    global _BRIDGE, _ON_DEPSGRAPH_UPDATE

    if _ON_DEPSGRAPH_UPDATE:
        return
    _ON_DEPSGRAPH_UPDATE = True
    try:
        if is_malt_active() == False:
            # Don't do anything if Malt is not the active renderer,
            # but make sure we setup all IDs the next time Malt is enabled
            _BRIDGE = None
            return
        
        sync_pipeline_settings()

        if _BRIDGE is None:
            scene.world.malt.update_pipeline(bpy.context)
            return

        ids = []
        class_data_map = {
            bpy.types.Scene : bpy.data.scenes,
            bpy.types.World : bpy.data.worlds,
            bpy.types.Camera : bpy.data.cameras,
            bpy.types.Object : bpy.data.objects,
            bpy.types.Material : bpy.data.materials,
            bpy.types.Mesh : bpy.data.meshes,
            bpy.types.Curve : bpy.data.curves,
            bpy.types.MetaBall : bpy.data.metaballs,
            bpy.types.Light : bpy.data.lights,
        }
        for update in depsgraph.updates:
            # Try to avoid as much re-setups as possible. 
            # Ideally we would do it only on ID creation.
            if update.is_updated_geometry == True or update.is_updated_transform == False:
                for cls, data in class_data_map.items():
                    if isinstance(update.id, cls):
                        ids.append(data[update.id.name])
        setup_parameters(ids)

        from . MaltNodes.MaltNodeTree import MaltTree

        redraw = False
        for update in depsgraph.updates:
            if update.is_updated_geometry:
                if isinstance(update.id, bpy.types.Object):
                    MaltMeshes.unload_mesh(update.id)
            if isinstance(update.id, bpy.types.Image):
                MaltTextures.unload_texture(update.id)
                redraw = True
            elif isinstance(update.id, bpy.types.Texture):
                MaltTextures.unload_gradients(update.id)
                redraw = True
            elif update.id.__class__.__name__ == 'MaltTree':
                redraw = True
        if redraw:
            for screen in bpy.data.screens:
                for area in screen.areas:
                    area.tag_redraw()
    except:
        import traceback
        traceback.print_exc()
    finally:
        _ON_DEPSGRAPH_UPDATE = False

@bpy.app.handlers.persistent
def load_scene(dummy1=None,dummy2=None):
    global _BRIDGE
    _BRIDGE = None

@bpy.app.handlers.persistent
def load_scene_post(dummy1=None,dummy2=None):
    from BlenderMalt.MaltNodes.MaltNodeTree import reset_subscriptions
    reset_subscriptions()
    if is_malt_active():
        bpy.context.scene.world.malt.update_pipeline(bpy.context)

__SAVE_PATH = None
@bpy.app.handlers.persistent
def save_pre(dummy1=None,dummy2=None):
    global __SAVE_PATH
    __SAVE_PATH = bpy.data.filepath

@bpy.app.handlers.persistent
def save_post(dummy1=None,dummy2=None):
    if __SAVE_PATH != bpy.data.filepath:
        load_scene_post()

def track_pipeline_changes():
    if is_malt_active() == False:
        return 1
    try:
        scene = bpy.context.scene
        malt = scene.world.malt
        path = bpy.path.abspath(malt.pipeline, library=malt.id_data.library)
        if os.path.exists(path):
            stats = os.stat(path)
            if stats.st_mtime > _TIMESTAMP:
                malt.update_pipeline(bpy.context)
    except:
        import traceback
        print(traceback.format_exc())

    return 1

def register():
    for _class in classes: bpy.utils.register_class(_class)
    bpy.types.World.malt = bpy.props.PointerProperty(type=MaltPipeline,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update)
    bpy.app.handlers.load_pre.append(load_scene)
    bpy.app.handlers.load_post.append(load_scene_post)
    bpy.app.handlers.save_pre.append(save_pre)
    bpy.app.handlers.save_post.append(save_post)
    bpy.app.timers.register(track_pipeline_changes, persistent=True)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)
    del bpy.types.World.malt
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update)
    bpy.app.handlers.load_pre.remove(load_scene)
    bpy.app.handlers.load_post.remove(load_scene_post)
    bpy.app.handlers.save_pre.remove(save_pre)
    bpy.app.handlers.save_post.remove(save_post)
    bpy.app.timers.unregister(track_pipeline_changes)

