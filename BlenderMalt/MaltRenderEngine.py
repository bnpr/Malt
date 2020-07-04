# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from itertools import chain

import bpy

from mathutils import Vector,Matrix,Quaternion

from .Malt.PipelineTest import PipelineTest
from .Malt.Mesh import Mesh
from .Malt import GL
from .Malt import Scene

from . import MaltPipeline
from . import MaltMeshes

class MaltRenderEngine(bpy.types.RenderEngine):
    # These three members are used by blender to set up the
    # RenderEngine; define its internal name, visible name and capabilities.
    bl_idname = "MALT"
    bl_label = "Malt"
    bl_use_preview = False

    # Init is called whenever a new render engine instance is created. Multiple
    # instances may exist at the same time, for example for a viewport and final
    # render.
    def __init__(self):
        self.first_update = True
        self.display_draw = None
        self.meshes = {}

    def __del__(self):
        pass

    def get_pipeline(self):
        return MaltPipeline.get_pipeline()
    
    def load_scene(self, context, depsgraph):

        def flatten_matrix(matrix):
            return list(chain.from_iterable(matrix.transposed()))

        scene = Scene.Scene()
        
        #Camera
        view_3d = context.region_data 
        camera_matrix = flatten_matrix(view_3d.view_matrix)
        projection_matrix = flatten_matrix(view_3d.window_matrix)
        scene.camera = Scene.Camera(camera_matrix, projection_matrix)

        #Objects
        materials = {}
        def add_object(obj, matrix):
            if obj.type in ('MESH','CURVE','SURFACE','FONT'):
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

                mesh = MaltMeshes.get_mesh(obj)
                matrix = flatten_matrix(matrix)
                scene.objects.append(Scene.Object(matrix, mesh, material, obj.malt_parameters.get_parameters()))
           
            elif obj.type == 'LIGHT':
                malt_light = obj.data.malt
                color = malt_light.color[:]
                position = obj.matrix_world.translation[:]
                direction = (obj.matrix_world.to_quaternion() @ Vector((0.0,0.0,-1.0)))[:]
                parameters = obj.malt_parameters.get_parameters()
                
                if obj.data.type == 'SUN':
                    scene.sun_lights.append(
                        Scene.SunLight(direction,color,parameters)
                    )
                
                elif obj.data.type == 'POINT':
                    scene.point_lights.append(
                        Scene.PointLight(position, malt_light.radius, color, parameters)
                    )
                
                elif obj.data.type == 'SPOT':
                    scene.spot_lights.append(
                        Scene.SpotLight(position, direction, malt_light.spot_angle, malt_light.spot_blend_angle, 
                        malt_light.radius, color, parameters)
                    )

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
        scene = depsgraph.scene
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)

        # Fill the render result with a flat color. The framebuffer is
        # defined as a list of pixels, each pixel itself being a list of
        # R,G,B,A values.
        if self.is_preview:
            color = [0.1, 0.2, 0.1, 1.0]
        else:
            color = [0.2, 0.1, 0.1, 1.0]

        pixel_count = self.size_x * self.size_y
        rect = [color] * pixel_count

        # Here we write the pixel values to the RenderResult
        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        layer.rect = rect
        self.end_result(result)

    # For viewport renders, this method gets called once at the start and
    # whenever the scene or 3D viewport changes. This method is where data
    # should be read from Blender in the same thread. Typically a render
    # thread will be started to do the work while keeping Blender responsive.
    def view_update(self, context, depsgraph):
        #MAKE SURE WE LOAD MESHES FROM HERE SINCE THEY ARE ALREADY EVALUATED
        #TODO: Optionally update only in object mode
        if self.first_update:
            # First time initialization
            self.first_update = False
            # Loop over all datablocks used in the scene.
            for datablock in depsgraph.ids:
                if datablock.__class__  is bpy.types.Object and datablock.type == 'MESH':
                    MaltMeshes.get_mesh(datablock)
        else:
            # Test which datablocks changed
            for update in depsgraph.updates:
                if update.id.__class__  is bpy.types.Object and update.id.type == 'MESH':
                    MaltMeshes.get_mesh(update.id)

    # For viewport renders, this method is called whenever Blender redraws
    # the 3D viewport. The renderer is expected to quickly draw the render
    # with OpenGL, and not perform other expensive work.
    # Blender will draw overlays for selection and editing on top of the
    # rendered image automatically.
    def view_draw(self, context, depsgraph):
        # Get viewport resolution
        resolution = context.region.width, context.region.height
        
        def bind_display_shader():
            self.bind_display_space_shader(depsgraph.scene)
        
        if self.display_draw is None or self.display_draw.resolution != resolution:
            self.display_draw = DisplayDraw(bind_display_shader, resolution)
        
        #Save FBO for later use
        fbo = GL.gl_buffer(GL.GL_INT, 1)
        GL.glGetIntegerv(GL.GL_FRAMEBUFFER_BINDING, fbo)
        
        #render
        scene = self.load_scene(context, depsgraph)
        render_texture = self.get_pipeline().render(resolution, scene)

        #Render to viewport
        self.display_draw.draw(bind_display_shader, fbo, render_texture)


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
        GL.glDeleteBuffers(2, self.vertex_buffer)
        GL.glDeleteVertexArrays(1, self.vertex_array)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

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
