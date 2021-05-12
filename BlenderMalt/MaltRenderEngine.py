# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import ctypes
import cProfile, pstats, io
import bpy
from mathutils import Vector,Matrix,Quaternion
from Malt import Scene
from Malt.GL import GL
from Malt.GL.Texture import Texture
from . import MaltPipeline, MaltMeshes, MaltMaterial, CBlenderMalt

PROFILE = False

class MaltRenderEngine(bpy.types.RenderEngine):
    # These three members are used by blender to set up the
    # RenderEngine; define its internal name, visible name and capabilities.
    bl_idname = "MALT"
    bl_label = "Malt"
    bl_use_preview = False
    bl_use_postprocess = True
    bl_use_shading_nodes_custom = False

    # Init is called whenever a new render engine instance is created. Multiple
    # instances may exist at the same time, for example for a viewport and final
    # render.
    def __init__(self):
        self.display_draw = None
        self.scene = Scene.Scene()
        self.view_matrix = None
        self.request_new_frame = True
        self.request_scene_update = True
        self.profiling_data = io.StringIO()
        self.bridge = MaltPipeline.get_bridge()
        self.bridge_id = self.bridge.get_viewport_id() if self.bridge else None

    def __del__(self):
        try:
            self.bridge.free_viewport_id(self.bridge_id)
            self.bridge = None
        except:
            # Sometimes Blender seems to call the destructor on unitialiazed instances (???)
            pass
    
    def get_scene(self, context, depsgraph, request_scene_update, overrides):
        def flatten_matrix(matrix):
            return [e for v in matrix.transposed() for e in v]
        
        materials = {}
        meshes = {}
        resources = {
            'materials': materials,
        }
        
        if request_scene_update == True:
            scene = Scene.Scene()
            self.scene = scene
        scene = self.scene
        scene.parameters = depsgraph.scene_eval.malt_parameters.get_parameters(overrides, resources)
        scene.world_parameters = depsgraph.scene_eval.world.malt_parameters.get_parameters(overrides, resources)

        scene.frame = depsgraph.scene_eval.frame_current
        r = depsgraph.scene_eval.render
        fps = r.fps / r.fps_base
        remap = r.frame_map_new / r.frame_map_old
        scene.time = (scene.frame / fps) * remap
        
        #Camera
        if depsgraph.mode == 'VIEWPORT':
            view_3d = context.region_data 
            camera_matrix = flatten_matrix(view_3d.view_matrix)
            projection_matrix = flatten_matrix(view_3d.window_matrix)
            if view_3d.perspective_matrix != self.view_matrix:
                self.view_matrix = view_3d.perspective_matrix.copy()
                self.request_new_frame = True
            scene.camera = Scene.Camera(camera_matrix, projection_matrix)
        else:
            camera = depsgraph.scene_eval.camera
            camera_matrix = flatten_matrix(camera.matrix_world.inverted())
            projection_matrix = flatten_matrix(
                camera.calc_matrix_camera( depsgraph, 
                    x=depsgraph.scene_eval.render.resolution_x, 
                    y=depsgraph.scene_eval.render.resolution_y
            ))
            scene.camera = Scene.Camera(camera_matrix, projection_matrix)
        
        if request_scene_update == False:
            return scene

        #Objects
        def add_object(obj, matrix):
            if obj.display_type in ['TEXTURED','SOLID'] and obj.type in ('MESH','CURVE','SURFACE','FONT'):
                name = MaltMeshes.get_mesh_name(obj)
                if depsgraph.mode == 'RENDER':
                    name = '___F12___' + name
                
                if name not in meshes:
                    # (Uses obj.original) Malt Parameters are not present in the evaluated mesh
                    parameters = obj.original.data.malt_parameters.get_parameters(overrides, resources)
                    malt_mesh = None
                    
                    if depsgraph.mode == 'VIEWPORT':
                        malt_mesh = MaltMeshes.get_mesh(obj)
                    else: #always load the mesh for final renders
                        malt_mesh = MaltMeshes.load_mesh(obj, name)
                    
                    if malt_mesh:
                        meshes[name] = [Scene.Mesh(submesh, parameters) for submesh in malt_mesh]
                    else:
                        meshes[name] = None

                mesh = meshes[name]
                if mesh is None:
                    return
                
                scale = matrix.to_scale()
                mirror_scale = scale[0]*scale[1]*scale[2] < 0.0
                matrix = flatten_matrix(matrix)

                obj_parameters = obj.malt_parameters.get_parameters(overrides, resources)
                
                if len(obj.material_slots) > 0:
                    for i, slot in enumerate(obj.material_slots):
                        material = None
                        if slot.material:
                            material_name = slot.material.name_full
                            if material_name not in materials.keys():
                                shader = {
                                    'path': slot.material.malt.get_source_path(),
                                    'parameters': slot.material.malt.parameters.get_parameters(overrides, resources)
                                }
                                parameters = slot.material.malt_parameters.get_parameters(overrides, resources)
                                materials[material_name] = Scene.Material(shader, parameters)
                            material = materials[material_name]
                        result = Scene.Object(matrix, mesh[i], material, obj_parameters, mirror_scale)
                        scene.objects.append(result)
                else:
                    result = Scene.Object(matrix, mesh[0], None, obj_parameters, mirror_scale)
                    scene.objects.append(result)
           
            elif obj.type == 'LIGHT':
                if obj.data.type == 'AREA':
                    return #Not supported

                malt_light = obj.data.malt

                light = Scene.Light()
                light.color = tuple(malt_light.color)
                light.position = tuple(obj.matrix_world.translation)
                light.direction = tuple(obj.matrix_world.to_quaternion() @ Vector((0.0,0.0,-1.0)))
                light.radius = malt_light.radius
                light.spot_angle = malt_light.spot_angle
                light.spot_blend = malt_light.spot_blend_angle
                light.parameters = obj.data.malt_parameters.get_parameters(overrides, resources)

                types = {
                    'SUN' : 1,
                    'POINT' : 2,
                    'SPOT' : 3,
                }
                light.type = types[obj.data.type]

                if light.type == types['SUN']:
                    light.matrix = flatten_matrix(matrix.to_quaternion().to_matrix().to_4x4().inverted())
                else:
                    #Scaling too ????
                    light.matrix = flatten_matrix(matrix.inverted())
                
                scene.lights.append(light)

        is_f12 = depsgraph.mode == 'RENDER'

        for obj in depsgraph.objects:
            if is_f12 or obj.visible_in_viewport_get(context.space_data):
                add_object(obj, obj.matrix_world)

        for instance in depsgraph.object_instances:
            if instance.instance_object:
                if is_f12 or instance.parent.visible_in_viewport_get(context.space_data):
                    add_object(instance.instance_object, instance.matrix_world)
        
        #TODO: 
        for i, obj in enumerate(scene.objects):
            obj.parameters['ID'] = i+1
        
        scene.meshes = list(meshes.values())
        scene.materials = list(materials.values())
        
        return scene
    
    def update_render_passes(self, scene=None, renderlayer=None):
        self.register_pass(scene, renderlayer, "Combined", 4, "RGBA", 'COLOR')
        self.register_pass(scene, renderlayer, "Depth", 1, "R", 'VALUE')

    def render(self, depsgraph):
        scene = depsgraph.scene_eval
        scale = scene.render.resolution_percentage / 100.0

        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)
        resolution = (self.size_x, self.size_y)

        overrides = ['Final Render']

        if self.bridge is not MaltPipeline.get_bridge(depsgraph.scene.world):
            self.bridge = MaltPipeline.get_bridge()
            self.bridge_id = self.bridge.get_viewport_id()
        
        MaltMaterial.track_shader_changes(force_update=True, async_compilation=False)

        scene = self.get_scene(None, depsgraph, True, overrides)
        MaltPipeline.get_bridge().render(0, resolution, scene, True)

        buffers = None
        finished = False

        import time
        while not finished:
            buffers, finished, read_resolution = MaltPipeline.get_bridge().render_result(0)
            time.sleep(0.1)
            if finished: break
        
        size = self.size_x * self.size_y

        result = self.begin_result(0, 0, self.size_x, self.size_y, layer=depsgraph.view_layer.name)
        passes = result.layers[0].passes

        if 'Combined' in passes:
            combined_pass = passes['Combined']
            rect_ptr = CBlenderMalt.get_rect_ptr(combined_pass.as_pointer())
            ctypes.memmove(rect_ptr, buffers['COLOR'], size*4*4)

        if 'Depth' in passes:
            depth_pass = passes['Depth']
            rect_ptr = CBlenderMalt.get_rect_ptr(depth_pass.as_pointer())
            ctypes.memmove(rect_ptr, buffers['DEPTH'], size*4)
        
        self.end_result(result)
        # Delete the scene. Otherwise we get memory leaks.
        # Blender never deletes RenderEngine instances ???
        del self.scene

    # For viewport renders, this method gets called once at the start and
    # whenever the scene or 3D viewport changes. This method is where data
    # should be read from Blender in the same thread. Typically a render
    # thread will be started to do the work while keeping Blender responsive.
    def view_update(self, context, depsgraph):
        self.request_new_frame = True
        self.request_scene_update = True

        # Test which datablocks changed
        for update in depsgraph.updates:
            if update.is_updated_geometry:
                if 'Object' in str(update.id.__class__):
                    MaltMeshes.unload_mesh(update.id)

    # For viewport renders, this method is called whenever Blender redraws
    # the 3D viewport. The renderer is expected to quickly draw the render
    # with OpenGL, and not perform other expensive work.
    # Blender will draw overlays for selection and editing on top of the
    # rendered image automatically.
    def view_draw(self, context, depsgraph):
        profiler = cProfile.Profile()
        global PROFILE
        if PROFILE:
            profiler.enable()
            if self.request_new_frame:
                self.profiling_data = io.StringIO()
        
        if self.bridge is not MaltPipeline.get_bridge():
            #The Bridge has been reset
            self.bridge = MaltPipeline.get_bridge()
            self.bridge_id = self.bridge.get_viewport_id()
            self.request_new_frame = True
            self.request_scene_update = True
        
        overrides = []
        if context.space_data.shading.type == 'MATERIAL':
            overrides.append('Preview')

        scene = self.get_scene(context, depsgraph, self.request_scene_update, overrides)
        resolution = context.region.width, context.region.height

        if self.request_new_frame:
            self.bridge.render(self.bridge_id, resolution, scene, self.request_scene_update)
            self.request_new_frame = False
            self.request_scene_update = False

        buffers, finished, read_resolution = self.bridge.render_result(self.bridge_id)
        pixels = buffers['COLOR']

        if not finished:
            self.tag_redraw()
        if pixels is None or resolution != read_resolution:
            # Only render if resolution is the same as read_resolution.
            # This avoids visual glitches when the viewport is resizing.
            # The alternative would be locking when writing/reading the pixel buffer.
            return
        
        for region in context.area.regions:
            if region.type == 'UI':
                region.tag_redraw()

        fbo = GL.gl_buffer(GL.GL_INT, 1)
        GL.glGetIntegerv(GL.GL_FRAMEBUFFER_BINDING, fbo)
        
        render_texture = Texture(resolution, GL.GL_RGBA32F, GL.GL_FLOAT, pixels)
        
        self.bind_display_space_shader(depsgraph.scene_eval)
        if self.display_draw is None or self.display_draw.resolution != resolution:
            if self.display_draw:
                self.display_draw.gl_delete()
            self.display_draw = DisplayDraw(resolution)
        self.display_draw.draw(fbo, render_texture)
        self.unbind_display_space_shader()

        if PROFILE:
            profiler.disable()
            stats = pstats.Stats(profiler, stream=self.profiling_data)
            stats.strip_dirs()
            stats.sort_stats(pstats.SortKey.CUMULATIVE)
            stats.print_stats()
            print('PROFILE BEGIN--------------------------------------')
            print(self.profiling_data.getvalue())
            print('PROFILE END--------------------------------------')

#Boilerplate code to draw an OpenGL texture to the viewport using Blender color management
class DisplayDraw(object):
    def __init__(self, resolution):
        self.resolution = resolution
        width, height = resolution

        shader_program = GL.gl_buffer(GL.GL_INT, 1)
        GL.glGetIntegerv(GL.GL_CURRENT_PROGRAM, shader_program)

        self.vertex_array = GL.gl_buffer(GL.GL_INT, 1)
        GL.glGenVertexArrays(1, self.vertex_array)
        GL.glBindVertexArray(self.vertex_array[0])

        texturecoord_location = GL.glGetAttribLocation(shader_program[0], "texCoord")
        position_location = GL.glGetAttribLocation(shader_program[0], "pos")

        GL.glEnableVertexAttribArray(texturecoord_location)
        GL.glEnableVertexAttribArray(position_location)

        position = [0.0, 0.0, width, 0.0, width, height, 0.0, height]
        position = GL.gl_buffer(GL.GL_FLOAT, len(position), position)
        texcoord = [0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0]
        texcoord = GL.gl_buffer(GL.GL_FLOAT, len(texcoord), texcoord)

        self.vertex_buffer = GL.gl_buffer(GL.GL_INT, 2)

        GL.glGenBuffers(2, self.vertex_buffer)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer[0])
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 32, position, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(position_location, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer[1])
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 32, texcoord, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(texturecoord_location, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def __del__(self):
        # We can't guarantee that the descructor runs on the correct OpenGL context.
        # This can cause driver crashes.
        # So it's better to just return early and let the memory leak. :(
        return
        self.gl_delete()
    
    def gl_delete(self):
        GL.glDeleteBuffers(2, self.vertex_buffer)
        GL.glDeleteVertexArrays(1, self.vertex_array)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def draw(self, fbo, texture):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo[0])
        GL.glActiveTexture(GL.GL_TEXTURE0)
        texture.bind()
        GL.glBindVertexArray(self.vertex_array[0])
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 4)
        GL.glBindVertexArray(0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)


import bpy_extras

class OT_MaltProfileFrameReport(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "wm.malt_profile_frame_report"
    bl_label = "Malt Profile Frame Report"

    filename_ext = ".txt"  # ExportHelper mixin class uses this

    filter_glob : bpy.props.StringProperty(
        default="*.txt",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        global REPORT_PATH
        REPORT_PATH = self.filepath
        global PROFILE
        PROFILE = True
        context.space_data.shading.type = 'SOLID'
        context.space_data.shading.type = 'RENDERED'
        return{'FINISHED'}

classes = [
    MaltRenderEngine,
    OT_MaltProfileFrameReport,
]

# RenderEngines also need to tell UI Panels that they are compatible with.
# We recommend to enable all panels marked as BLENDER_RENDER, and then
# exclude any panels that are replaced by Malt panels registered by the
# render engine, or that are not supported.
def get_panels():
    exclude_panels = {
        'VIEWLAYER_PT_filter',
        'VIEWLAYER_PT_layer_passes',
        'DATA_PT_area',
    }

    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for panel in get_panels():
        panel.COMPAT_ENGINES.add('MALT')

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for panel in get_panels():
        if 'MALT' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('MALT')

if __name__ == "__main__":
    register()
