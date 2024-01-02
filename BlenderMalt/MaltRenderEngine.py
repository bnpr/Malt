import ctypes, time, platform
import xxhash
import bpy
from mathutils import Vector, Matrix, Quaternion
from Malt import Scene
from Malt.Pipeline import SHADER_DIR
from Malt.GL import GL
from Malt.GL.Texture import Texture
from Malt.GL.Shader import Shader, shader_preprocessor
from Malt.GL.Mesh import Mesh
from . import MaltPipeline, MaltMeshes, MaltMaterial, CBlenderMalt

CAPTURE = False

WINM = None
if platform.system() == 'Windows':
    WINM = ctypes.WinDLL('winmm')

def high_res_sleep(seconds):
    if WINM:
        WINM.timeBeginPeriod(1)
        time.sleep(seconds)
        WINM.timeEndPeriod(1)
    else:
        time.sleep(seconds)


class MaltRenderEngine(bpy.types.RenderEngine):
    bl_idname = "MALT"
    bl_label = "Malt"
    bl_use_preview = False
    bl_use_postprocess = True
    bl_use_shading_nodes_custom = False

    def __init__(self):
        self.display_draw = None
        self.scene = Scene.Scene()
        self.view_matrix = None
        self.request_new_frame = True
        self.request_scene_update = True
        self.bridge = MaltPipeline.get_bridge()
        self.bridge_id = self.bridge.get_viewport_id() if self.bridge else None
        self.last_frame_time = 0

    def __del__(self):
        try:
            self.bridge.free_viewport_id(self.bridge_id)
            self.bridge = None
        except:
            # Sometimes Blender seems to call the destructor on unitialiazed instances (???)
            pass
    
    def get_scene(self, context, depsgraph, request_scene_update, overrides):
        if request_scene_update == True:
            scene = Scene.Scene()
            self.scene = scene
        scene = self.scene
        
        if hasattr(scene, 'proxys') == False:
            scene.proxys = {}

        scene.parameters = depsgraph.scene_eval.malt_parameters.get_parameters(overrides, scene.proxys)
        scene.world_parameters = depsgraph.scene_eval.world.malt_parameters.get_parameters(overrides, scene.proxys)

        override_material = scene.world_parameters['Material.Override']
        default_material = scene.world_parameters['Material.Default']

        scene.frame = depsgraph.scene_eval.frame_current
        r = depsgraph.scene_eval.render
        fps = r.fps / r.fps_base
        remap = r.frame_map_new / r.frame_map_old
        scene.time = (scene.frame / fps) * remap
        
        def flatten_matrix(matrix):
            return [e for v in matrix.transposed() for e in v]
        
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
        
        meshes = {}

        #Objects
        def add_object(obj, matrix, id):
            if obj.type in ('MESH','CURVE','SURFACE','META', 'FONT'):
                name = MaltMeshes.get_mesh_name(obj)
                if depsgraph.mode == 'RENDER':
                    name = '___F12___' + name
                
                if name not in meshes:
                    # (Uses obj.original) Malt Parameters are not present in the evaluated mesh
                    parameters = obj.original.data.malt_parameters.get_parameters(overrides, scene.proxys)
                    malt_mesh = None
                    
                    if depsgraph.mode == 'VIEWPORT':
                        malt_mesh = MaltMeshes.get_mesh(obj)
                    else: #always load the mesh for final renders
                        malt_mesh = MaltMeshes.load_mesh(obj, name)
                    
                    if malt_mesh:
                        meshes[name] = [Scene.Mesh(submesh, parameters) for submesh in malt_mesh]
                        for i, mesh in enumerate(meshes[name]):
                            scene.proxys[('mesh',name,i)] = mesh.mesh
                    else:
                        meshes[name] = None

                mesh = meshes[name]
                if mesh is None:
                    return
                
                scale = matrix.to_scale()
                mirror_scale = scale[0]*scale[1]*scale[2] < 0.0
                matrix = flatten_matrix(matrix)

                obj_parameters = obj.malt_parameters.get_parameters(overrides, scene.proxys)
                obj_parameters['ID'] = id

                tags = set(collection.name for collection in obj.original.users_collection)
                
                if len(obj.material_slots) > 0:
                    for i, slot in enumerate(obj.material_slots):
                        material = default_material
                        if slot.material and slot.material.malt.get_source_path() != '':
                            material_name = slot.material.name_full
                            material_key = ('material',material_name)
                            if material_key not in scene.proxys.keys():
                                path = slot.material.malt.get_source_path()
                                shader_parameters = slot.material.malt.get_parameters(overrides, scene.proxys)
                                material_parameters = slot.material.malt_parameters.get_parameters(overrides, scene.proxys)
                                from Bridge.Proxys import MaterialProxy
                                scene.proxys[material_key]  = MaterialProxy(path, shader_parameters, material_parameters)
                            material = scene.proxys[material_key]
                        if override_material: material = override_material
                        result = Scene.Object(matrix, mesh[i], material, obj_parameters, mirror_scale, tags)
                        scene.objects.append(result)
                else:
                    material = default_material
                    if override_material: material = override_material
                    result = Scene.Object(matrix, mesh[0], material, obj_parameters, mirror_scale, tags)
                    scene.objects.append(result)
           
            elif obj.type == 'LIGHT':
                if obj.data.type == 'AREA':
                    return #Not supported

                malt_light = obj.data.malt

                light = Scene.Light()
                light.color = tuple(obj.data.color * malt_light.strength)
                light.position = tuple(matrix.translation)
                light.direction = tuple(matrix.to_quaternion() @ Vector((0.0,0.0,-1.0)))
                if malt_light.override_global_settings:
                    light.sun_max_distance = malt_light.max_distance
                light.radius = malt_light.radius
                light.spot_angle = malt_light.spot_angle
                light.spot_blend = malt_light.spot_blend_angle
                light.parameters = obj.data.malt_parameters.get_parameters(overrides, scene.proxys)

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

        def visible_display(obj):
            return obj.display_type in ('TEXTURED','SOLID') or obj.type == 'LIGHT'

        for obj in depsgraph.objects:
            if is_f12 or (visible_display(obj) and obj.visible_in_viewport_get(context.space_data)):
                id = xxhash.xxh3_64_intdigest(obj.name_full.encode()) % (2**16)
                add_object(obj, obj.matrix_world, id)

        for instance in depsgraph.object_instances:
            if instance.instance_object:
                obj = instance.instance_object
                parent = instance.parent
                if is_f12 or (visible_display(obj) and visible_display(parent) and
                parent.visible_in_viewport_get(context.space_data)):
                    id = abs(instance.random_id) % (2**16)
                    add_object(instance.instance_object, instance.matrix_world, id)
        
        return scene
    
    def get_AOVs(self, scene):
        #TODO: Hardcoded for now
        result = {}
        try:
            render_tree = scene.world.malt_parameters.graphs['Render'].graph
            for io in render_tree.get_custom_io('Render'):
                if io['io'] in ['out', 'inout'] and io['type'] == 'Texture':
                    result[io['name']] = GL.GL_RGBA32F
        except:
            import traceback
            traceback.print_exc()
        return result        
    
    def update_render_passes(self, scene=None, renderlayer=None):
        bridge = MaltPipeline.get_bridge(scene.world, True)
        render_outputs = bridge.render_outputs
        if 'COLOR' in render_outputs.keys():
            self.register_pass(scene, renderlayer, "Combined", 4, "RGBA", 'COLOR')
        if 'DEPTH' in render_outputs.keys():
            self.register_pass(scene, renderlayer, "Depth", 1, "R", 'VALUE')
        from itertools import chain
        for output, format in chain(render_outputs.items(), self.get_AOVs(scene).items()):
            if output not in ('COLOR', 'DEPTH'):
                #TODO: 'COLOR' vs 'VECTOR' ???
                self.register_pass(scene, renderlayer, output, 4, "RGBA", 'COLOR')

    def render(self, depsgraph):
        scene = depsgraph.scene_eval
        scale = scene.render.resolution_percentage / 100.0

        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)
        resolution = (self.size_x, self.size_y)

        overrides = ['Final Render']

        bridge = MaltPipeline.get_bridge(depsgraph.scene.world, True)
        if self.bridge is not bridge:
            self.bridge = bridge
            self.bridge_id = self.bridge.get_viewport_id()
        
        MaltMaterial.track_shader_changes(force_update=True, async_compilation=False)

        AOVs = self.get_AOVs(scene)
        scene = self.get_scene(None, depsgraph, True, overrides)
        self.bridge.render(0, resolution, scene, True, AOVs=AOVs)

        buffers = None
        finished = False

        import time
        while not finished:
            buffers, finished, read_resolution = self.bridge.render_result(0)
            time.sleep(0.1)
            if finished: break
        
        size = self.size_x * self.size_y

        from itertools import chain
        for output in chain(self.bridge.render_outputs.keys(), AOVs.keys()):
            if output not in ('COLOR', 'DEPTH'):
                self.add_pass(output, 4, 'RGBA')
        
        result = self.begin_result(0, 0, self.size_x, self.size_y, layer=depsgraph.view_layer.name)
        passes = result.layers[0].passes
        
        for key, value in passes.items():
            buffer_name = key
            if key == 'Combined': buffer_name = 'COLOR'
            if key == 'Depth': buffer_name = 'DEPTH'
            if buffer_name in buffers and hasattr(buffers[buffer_name], 'buffer'):
                value.rect = buffers[buffer_name].as_np_array((size , value.channels))
        
        self.end_result(result)
        # Delete the scene. Otherwise we get memory leaks.
        # Blender never deletes RenderEngine instances ???
        del self.scene

    def view_update(self, context, depsgraph):
        self.request_new_frame = True
        self.request_scene_update = True

        for update in depsgraph.updates:
            if update.is_updated_geometry:
                if isinstance(update.id, bpy.types.Object):
                    MaltMeshes.unload_mesh(update.id)

    def view_draw(self, context, depsgraph):
        if self.bridge is not MaltPipeline.get_bridge():
            #The Bridge has been reset
            self.bridge = MaltPipeline.get_bridge()
            self.bridge_id = self.bridge.get_viewport_id()
            self.request_new_frame = True
            self.request_scene_update = True
        
        global CAPTURE
        if CAPTURE:
            self.request_new_frame = True
        
        overrides = []
        if context.space_data.shading.type == 'MATERIAL':
            overrides.append('Preview')

        scene = self.get_scene(context, depsgraph, self.request_scene_update, overrides)
        viewport_resolution = context.region.width, context.region.height
        resolution = viewport_resolution

        resolution_scale = scene.world_parameters['Viewport.Resolution Scale']
        mag_filter = GL.GL_LINEAR
        if resolution_scale != 1.0:
            w,h = resolution
            resolution = round(w*resolution_scale), round(h*resolution_scale)
            smooth_interpolation = scene.world_parameters['Viewport.Smooth Interpolation']
            mag_filter = GL.GL_LINEAR if smooth_interpolation else GL.GL_NEAREST

        if self.request_new_frame:
            self.bridge.render(self.bridge_id, resolution, scene, self.request_scene_update, CAPTURE)
            CAPTURE = False
            self.request_new_frame = False
            self.request_scene_update = False
        
        target_fps = context.preferences.addons['BlenderMalt'].preferences.render_fps_cap
        if target_fps > 0:
            delta_time = time.perf_counter() - self.last_frame_time
            target_delta = 1.0 / target_fps
            if delta_time < target_delta:
                high_res_sleep(target_delta - delta_time)
        
        self.last_frame_time = time.perf_counter() 

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

        data_format = GL.GL_FLOAT
        texture_format = GL.GL_RGBA32F
        if self.bridge.viewport_bit_depth == 8:
            data_format = GL.GL_UNSIGNED_BYTE
            texture_format = GL.GL_RGBA8
            if GL.glGetInternalformativ(GL.GL_TEXTURE_2D, texture_format, GL.GL_READ_PIXELS, 1) != GL.GL_ZERO:
                data_format = GL.glGetInternalformativ(GL.GL_TEXTURE_2D, texture_format, GL.GL_TEXTURE_IMAGE_TYPE, 1)
        elif self.bridge.viewport_bit_depth == 16:
            data_format = GL.GL_HALF_FLOAT
            texture_format = GL.GL_RGBA16F
        
        try:
            render_texture = Texture(resolution, texture_format, data_format, pixels.buffer(),
                mag_filter=mag_filter, pixel_format=GL.GL_RGBA)
        except:
            # Fallback to unsigned byte, just in case (matches Server behavior)
            render_texture = Texture(resolution, GL.GL_RGBA8, GL.GL_UNSIGNED_BYTE, pixels.buffer(),
                mag_filter=mag_filter)
        
        global DISPLAY_DRAW
        if DISPLAY_DRAW is None:
            DISPLAY_DRAW = DisplayDraw()
        DISPLAY_DRAW.draw(fbo, render_texture)

DISPLAY_DRAW = None

class DisplayDraw():
    def __init__(self):
        positions=[
             1.0,  1.0, 1.0,
             1.0, -1.0, 1.0,
            -1.0, -1.0, 1.0,
            -1.0,  1.0, 1.0,
        ]
        indices=[
            0, 1, 3,
            1, 2, 3,
        ]
        self.quad = Mesh(positions, indices)
        source='#include "Passes/sRGBConversion.glsl"'
        vertex_src = shader_preprocessor(source, [SHADER_DIR], ['VERTEX_SHADER'])
        pixel_src = shader_preprocessor(source, [SHADER_DIR], ['PIXEL_SHADER'])
        self.shader = Shader(vertex_src, pixel_src)

    def draw(self, fbo, texture):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo[0])
        self.shader.uniforms["to_srgb"].set_value(False)
        self.shader.uniforms["convert"].set_value(texture.internal_format == GL.GL_RGBA8)
        self.shader.textures["input_texture"] = texture
        self.shader.bind()
        self.quad.draw()


class OT_MaltRenderDocCapture(bpy.types.Operator):
    bl_idname = "wm.malt_renderdoc_capture"
    bl_label = "RenderDoc Capture"

    def execute(self, context):
        global CAPTURE
        CAPTURE = True
        context.area.tag_redraw()
        return {'FINISHED'}
    
class VIEW3D_PT_Malt_Stats(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "View"
    bl_label = "Malt Stats"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT'

    def draw(self, context):
        from . import MaltPipeline
        self.layout.operator("wm.malt_renderdoc_capture")
        stats = MaltPipeline.get_bridge().get_stats()
        for line in stats.splitlines():
            self.layout.label(text=line)

classes = [
    MaltRenderEngine,
    OT_MaltRenderDocCapture,
    VIEW3D_PT_Malt_Stats,
]

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
