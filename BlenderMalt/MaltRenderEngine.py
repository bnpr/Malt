# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from itertools import chain

import bpy

from mathutils import Vector,Matrix,Quaternion

from BlenderMalt import MaltMaterial
from Malt.PipelineTest import PipelineTest
from Malt.Mesh import Mesh
from Malt import GL
from Malt import Scene

from BlenderMalt import MaltPipeline
from BlenderMalt import MaltMeshes

class MaltRenderEngine(bpy.types.RenderEngine):
    # These three members are used by blender to set up the
    # RenderEngine; define its internal name, visible name and capabilities.
    bl_idname = "MALT"
    bl_label = "Malt"
    bl_use_preview = False
    bl_use_postprocess = True
    bl_use_shading_nodes_custom = False
    bl_use_gpu_context = True
    bl_use_eevee_freestyle = True

    # Init is called whenever a new render engine instance is created. Multiple
    # instances may exist at the same time, for example for a viewport and final
    # render.
    def __init__(self):
        self.display_draw = None
        self.meshes = {}
        self.pipeline = MaltPipeline.get_pipeline().__class__()
        self.view_matrix = None
        self.request_new_frame = False

    def __del__(self):
        pass

    def get_pipeline(self):
        if self.pipeline is None or self.pipeline.__class__ != MaltPipeline.get_pipeline().__class__:
            self.pipeline = MaltPipeline.get_pipeline().__class__()
        return self.pipeline
    
    def load_scene(self, context, depsgraph):

        def flatten_matrix(matrix):
            return list(chain.from_iterable(matrix.transposed()))

        scene = Scene.Scene()
        scene.parameters = depsgraph.scene_eval.malt_parameters.get_parameters()
        scene.world_parameters = depsgraph.scene_eval.world.malt_parameters.get_parameters()

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

        #Objects
        materials = {}
        meshes = {}

        def add_object(obj, matrix):
            if obj.display_type == 'TEXTURED' and obj.type in ('MESH','CURVE','SURFACE','FONT'):
                material = None
                if len(obj.material_slots) > 0 and obj.material_slots[0].material:
                    blend_material = obj.material_slots[0].material
                    material_name = blend_material.name_full
                    if material_name not in materials.keys():
                        #load material
                        shader = blend_material.malt.get_shader()
                        if shader:
                            pipeline_shaders = shader[self.get_pipeline().__class__.__name__]
                            parameters = blend_material.malt_parameters.get_parameters()
                            materials[material_name] = Scene.Material(pipeline_shaders, parameters)
                        else:
                            materials[material_name] = None
                    material = materials[material_name]

                if obj.name_full not in meshes:
                    # (Uses obj.original) Malt Parameters are not present in the evaluated mesh
                    parameters = obj.original.data.malt_parameters.get_parameters()
                    meshes[obj.name_full] = Scene.Mesh(None, parameters)
                    if depsgraph.mode == 'VIEWPORT':
                        meshes[obj.name_full].mesh = MaltMeshes.get_mesh(obj)
                    else: #always load the mesh for final renders
                        meshes[obj.name_full].mesh = MaltMeshes.load_mesh(obj)

                mesh = meshes[obj.name_full]
                if mesh is None:
                    return
                scale = matrix.to_scale()
                matrix = flatten_matrix(matrix)
                result = Scene.Object(matrix, mesh, material, obj.malt_parameters.get_parameters())
                if scale[0]*scale[1]*scale[2] < 0.0:
                    result.negative_scale = True
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
                light.parameters = obj.malt_parameters.get_parameters()
                #Scaling too ????
                light.matrix = flatten_matrix(matrix.inverted())
                
                types = {
                    'SUN' : 1,
                    'POINT' : 2,
                    'SPOT' : 3,
                }
                light.type = types[obj.data.type]

                scene.lights.append(light)

        for obj in depsgraph.objects:
                add_object(obj, obj.matrix_world)
        
        for instance in depsgraph.object_instances:
            if instance.instance_object:
                add_object(instance.instance_object, instance.matrix_world)

        return scene

    # This is the method called by Blender for both final renders (F12) and
    # small preview for materials, world and lights.
    #TODO
    def render(self, depsgraph):
        scene = depsgraph.scene_eval
        scale = scene.render.resolution_percentage / 100.0

        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)
        resolution = (self.size_x, self.size_y)

        scene = self.load_scene(None, depsgraph)
        render_textures = None
        while True:
            render_textures = self.get_pipeline().render(resolution, scene, True, False)
            if self.get_pipeline().needs_more_samples() == False:
                break
        render_textures['COLOR'].bind()
        
        result = self.begin_result(0, 0, self.size_x, self.size_y)

        render_textures['COLOR'].bind()
        gl_pixels = GL.gl_buffer(GL.GL_FLOAT, resolution[0]*resolution[1]*4)
        GL.glGetTexImage(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, GL.GL_FLOAT, gl_pixels)
        it = iter(gl_pixels)
        pixels = list(zip(it,it,it,it)) #convert from 1D list to list of tuples

        layer = result.layers[0].passes["Combined"]
        layer.rect = pixels

        render_textures['DEPTH'].bind()
        gl_pixels = GL.gl_buffer(GL.GL_FLOAT, resolution[0]*resolution[1])
        GL.glGetTexImage(GL.GL_TEXTURE_2D, 0, GL.GL_RED, GL.GL_FLOAT, gl_pixels)

        layer = result.layers[0].passes["Depth"]
        layer.rect.foreach_set(list(gl_pixels))

        self.end_result(result)

        #Delete the pipeline while we are in the correct OpenGL context
        del self.pipeline


    # For viewport renders, this method gets called once at the start and
    # whenever the scene or 3D viewport changes. This method is where data
    # should be read from Blender in the same thread. Typically a render
    # thread will be started to do the work while keeping Blender responsive.
    def view_update(self, context, depsgraph):
        self.request_new_frame = True
        # Test which datablocks changed
        for update in depsgraph.updates:
            if update.is_updated_geometry:
                MaltMeshes.MESHES[update.id.name_full] = None

    # For viewport renders, this method is called whenever Blender redraws
    # the 3D viewport. The renderer is expected to quickly draw the render
    # with OpenGL, and not perform other expensive work.
    # Blender will draw overlays for selection and editing on top of the
    # rendered image automatically.
    def view_draw(self, context, depsgraph):
        # Get viewport resolution
        resolution = context.region.width, context.region.height
        
        def bind_display_shader():
            self.bind_display_space_shader(depsgraph.scene_eval)
        
        if self.display_draw is None or self.display_draw.resolution != resolution:
            self.display_draw = DisplayDraw(bind_display_shader, resolution)
        
        #Save FBO for later use
        fbo = GL.gl_buffer(GL.GL_INT, 1)
        GL.glGetIntegerv(GL.GL_FRAMEBUFFER_BINDING, fbo)

        # Generating a VAO before loading/rendering fixes an error where the viewport
        # freezes in edit mode. Why ??? I have no idea. ¯\_(ツ)_/¯
        # TODO: try to load meshes the normal way, without lazy VAO generation.
        # (Would need a Pipeline refactor)
        VAO = GL.gl_buffer(GL.GL_INT, 1)
        GL.glGenVertexArrays(1, VAO)
        
        #render
        scene = self.load_scene(context, depsgraph)
        render_texture = self.get_pipeline().render(resolution, scene, False, self.request_new_frame)['COLOR']
        self.request_new_frame = False
        if MaltMaterial.INITIALIZED == False: #First viewport render can happen before initialization
            self.request_new_frame = True

        #Render to viewport
        self.display_draw.draw(bind_display_shader, fbo, render_texture)

        if self.get_pipeline().needs_more_samples():
            self.tag_redraw()

        GL.glDeleteVertexArrays(1, VAO)


#Boilerplate code to draw an OpenGL texture to the viewport using Blender color management
class DisplayDraw(object):
    def __init__(self, bind_display_shader, resolution):
        # Generate dummy float image buffer
        self.resolution = resolution
        width, height = resolution

        bind_display_shader()
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
        try:
            GL.glDeleteBuffers(2, self.vertex_buffer)
            GL.glDeleteVertexArrays(1, self.vertex_array)
            GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        except:
            #TODO: Make sure GL objects are deleted in the correct context
            pass

    def draw(self, bind_display_shader, fbo, texture):
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)
        bind_display_shader()
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo[0])
        GL.glActiveTexture(GL.GL_TEXTURE0)
        texture.bind()
        GL.glBindVertexArray(self.vertex_array[0])
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, 4)
        GL.glBindVertexArray(0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

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
    bpy.utils.register_class(MaltRenderEngine)

    for panel in get_panels():
        panel.COMPAT_ENGINES.add('MALT')

def unregister():
    bpy.utils.unregister_class(MaltRenderEngine)

    for panel in get_panels():
        if 'MALT' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('MALT')

if __name__ == "__main__":
    register()
