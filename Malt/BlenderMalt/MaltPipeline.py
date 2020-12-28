# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy

from Malt.Pipeline import Pipeline

def get_subclasses(cls):
    subclasses = []
    for subclass in cls.__subclasses__():
        subclasses.append(subclass)
        subclasses.extend(get_subclasses(subclass))
    return subclasses

#TODO: We need to store more than 1 pipeline since it's possible to have more than
# one scene open at the same time with different worlds and render pipelines
__PIPELINE__ = None

def get_pipeline():
    global __PIPELINE__
    if __PIPELINE__ is None:
        #TODO: update pipeline on file loading
        bpy.context.scene.world.malt.update_pipeline(bpy.context)
    return __PIPELINE__

class MaltPipeline(bpy.types.PropertyGroup):

    def enum_pipelines(self, context):
        pipelines = []
        for _cls in get_subclasses(Pipeline):
            pipelines.append((_cls.__name__,_cls.__name__,""))
        #Enum needs at least 2 items to work
        while len(pipelines) < 2:
            pipelines.append(('---','---',''))
        return pipelines

    def update_pipeline(self, context):
        for _cls in get_subclasses(Pipeline):
            if _cls.__name__ == self.pipeline_class:
                global __PIPELINE__
                __PIPELINE__ = _cls()
                setup_all_ids()
    
    pipeline_class : bpy.props.EnumProperty(items=enum_pipelines, update=update_pipeline)

    def draw_ui(self, layout):
        layout.label(text="Malt Pipeline")
        layout.prop(self, "pipeline_class")


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

def setup_parameters(ids):
    pipeline_parameters = get_pipeline().get_parameters()

    class_parameters_map = {
        bpy.types.Scene : pipeline_parameters.scene,
        bpy.types.World : pipeline_parameters.world,
        bpy.types.Camera : pipeline_parameters.camera,
        bpy.types.Object : pipeline_parameters.object,
        bpy.types.Material : pipeline_parameters.material,
        bpy.types.Mesh : pipeline_parameters.mesh,
        bpy.types.Curve : pipeline_parameters.mesh,
        bpy.types.Light : pipeline_parameters.light,
    }

    for bid in ids:
        for cls, parameters in class_parameters_map.items():
            if isinstance(bid, cls):
                bid.malt_parameters.setup(parameters)


__INITIALIZED = False

def setup_all_ids():
    setup_parameters(bpy.data.scenes)
    setup_parameters(bpy.data.worlds)
    setup_parameters(bpy.data.cameras)
    setup_parameters(bpy.data.objects)
    setup_parameters(bpy.data.materials)
    setup_parameters(bpy.data.meshes)
    setup_parameters(bpy.data.curves)
    setup_parameters(bpy.data.lights)
    for material in bpy.data.materials:
        material.malt.update_source(bpy.context)
    global __INITIALIZED
    __INITIALIZED = True


@bpy.app.handlers.persistent
def depsgraph_update(scene, depsgraph):
    global __INITIALIZED

    if scene.render.engine != 'MALT':
        # Don't do anything if Malt is not the active renderer,
        # but make sure we setup all IDs the next time Malt is enabled
        __INITIALIZED = False
        return

    if __INITIALIZED == False:
        setup_all_ids()
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
        bpy.types.Light : bpy.data.lights,
    }
    for update in depsgraph.updates:
        if update.id.library is None: # Only local data
            # Try to avoid as much re-setups as possible. 
            # Ideally we would do it only on ID creation.
            if update.is_updated_geometry == True or update.is_updated_transform == False:
                for cls, data in class_data_map.items():
                    if isinstance(update.id, cls):
                        ids.append(data[update.id.name])
    setup_parameters(ids)
 
import sys
import os
from pathlib import Path
import importlib
import traceback
def load_malt_lib(path):
    p = Path(path)
    if str(p) not in sys.path:
        sys.path.append(str(p))
    for e in p.iterdir():
        try:
            if e.name == '__pycache__':
                continue
            name = e.name
            if e.is_file():
                name = name.split('.')[0]
            module = __import__(name)
            importlib.reload(module)
        except ModuleNotFoundError:
            # Ignore it. The file or dir is not a python module (glsl files, for example)
            pass
        except Exception:
            traceback.print_exc()

def register():
    for _class in classes: bpy.utils.register_class(_class)
    bpy.types.World.malt = bpy.props.PointerProperty(type=MaltPipeline)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update)

    malt_lib_path = bpy.context.preferences.addons['BlenderMalt'].preferences.malt_library_path

    if malt_lib_path != '':
        load_malt_lib(malt_lib_path)
        if malt_lib_path not in Pipeline.SHADER_INCLUDE_PATHS:
            Pipeline.SHADER_INCLUDE_PATHS.append(malt_lib_path)

def unregister():
    for _class in classes: bpy.utils.unregister_class(_class)
    del bpy.types.World.malt
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update)

