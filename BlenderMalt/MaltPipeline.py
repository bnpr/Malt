# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import os, platform, time
import bpy
from . import MaltMaterial, MaltMeshes, MaltTextures

__BRIDGE = None
__PIPELINE_PARAMETERS = None
TIMESTAMP = time.time()

def get_bridge(world=None, force_creation=False):
    global __BRIDGE
    bridge = __BRIDGE
    if (bridge and bridge.lost_connection) or (bridge is None and force_creation):
        __BRIDGE = None
        try:
            if world is None:
                bpy.context.scene.world.malt.update_pipeline(bpy.context)
            else:
                world.malt.update_pipeline(bpy.context)
        except:
            pass
    return __BRIDGE

def set_bridge(bridge):
    global __BRIDGE
    __BRIDGE = bridge

def set_pipeline_parameters(parameters):
    global __PIPELINE_PARAMETERS
    __PIPELINE_PARAMETERS = parameters

class MaltPipeline(bpy.types.PropertyGroup):

    def update_pipeline(self, context):
        global TIMESTAMP
        TIMESTAMP = time.time()
        
        #TODO: Sync all scenes. Only one active pipeline per Blender instance is supported atm.
        pipeline = self.pipeline
        if pipeline == '':
            current_dir = os.path.dirname(os.path.abspath(__file__))
            default_pipeline = os.path.join(current_dir,'.MaltPath','Malt','Pipelines','NPR_Pipeline','NPR_Pipeline_Nodes.py')
            if platform.system() == 'Darwin':
                # The NPR Pipeline doesn't work on OpenGL implementations limited to 16 sampler uniforms
                default_pipeline = os.path.join(current_dir,'.MaltPath','Malt','Pipelines','MiniPipeline','MiniPipeline.py')
            pipeline = default_pipeline

        debug_mode = bool(bpy.context.preferences.addons['BlenderMalt'].preferences.debug_mode)
        renderdoc_path = bpy.context.preferences.addons['BlenderMalt'].preferences.renderdoc_path
        
        path = bpy.path.abspath(pipeline, library=self.id_data.library)
        import Bridge
        bridge = Bridge.Client_API.Bridge(path, debug_mode, renderdoc_path)
        import logging as log
        log.info('Blender {} {} {}'.format(bpy.app.version_string, bpy.app.build_branch, bpy.app.build_hash))
        params = bridge.get_parameters()
        
        #BlenderMalt parameters
        from Malt import Parameter
        params.world['Viewport.Resolution Scale'] = Parameter.Parameter(1.0 , Parameter.Type.FLOAT)
        params.world['Viewport.Smooth Interpolation'] = Parameter.Parameter(True , Parameter.Type.BOOL)

        set_bridge(bridge)
        set_pipeline_parameters(params)
        
        self.graph_types.clear()
        for graph in bridge.graphs.keys():
            self.graph_types.add().name = graph
        
        MaltMaterial.reset_materials()
        MaltMeshes.reset_meshes()
        MaltTextures.reset_textures()

        setup_all_ids()
    
    pipeline : bpy.props.StringProperty(name="Malt Pipeline", subtype='FILE_PATH', update=update_pipeline)
    graph_types : bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    overrides : bpy.props.StringProperty(name='Pipeline Overrides', default='Preview,Final Render')

    def draw_ui(self, layout):
        layout.prop(self, 'pipeline')


class MALT_PT_Pipeline(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    bl_context = "world"
    bl_label = "Pipeline Settings"
    COMPAT_ENGINES = {'MALT'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT' and context.world is not None

    def draw(self, context):
        context.scene.world.malt.draw_ui(self.layout)

classes = (
    MaltPipeline,
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
    from BlenderMalt import MaltNodes
    MaltNodes.setup_node_trees()
    MaltMaterial.track_shader_changes(force_update=True)

def setup_parameters(ids):
    global __PIPELINE_PARAMETERS
    pipeline_parameters = __PIPELINE_PARAMETERS

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
        for cls, parameters in class_parameters_map.items():
            if isinstance(bid, cls):
                bid.malt_parameters.setup(parameters)


@bpy.app.handlers.persistent
def depsgraph_update(scene, depsgraph):
    global __BRIDGE

    if scene.render.engine != 'MALT':
        # Don't do anything if Malt is not the active renderer,
        # but make sure we setup all IDs the next time Malt is enabled
        __BRIDGE = None
        return

    if __BRIDGE is None:
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

    from . MaltNodes import MaltTree

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
        elif isinstance(update.id, MaltTree):
            redraw = True
    if redraw:
        for screen in bpy.data.screens:
            for area in screen.areas:
                area.tag_redraw()

@bpy.app.handlers.persistent
def load_scene(dummy1=None,dummy2=None):
    global __BRIDGE
    __BRIDGE = None

@bpy.app.handlers.persistent
def load_scene_post(dummy1=None,dummy2=None):
    if bpy.context.scene.render.engine == 'MALT':
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
    if bpy.context.scene.render.engine != 'MALT':
        return 1
    try:
        scene = bpy.context.scene
        malt = scene.world.malt
        path = bpy.path.abspath(malt.pipeline, library=malt.id_data.library)
        if os.path.exists(path):
            stats = os.stat(path)
            if stats.st_mtime > TIMESTAMP:
                malt.update_pipeline(bpy.context)
    except:
        import traceback
        print(traceback.format_exc())

    return 1

def register():
    for _class in classes: bpy.utils.register_class(_class)
    bpy.types.World.malt = bpy.props.PointerProperty(type=MaltPipeline)
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

