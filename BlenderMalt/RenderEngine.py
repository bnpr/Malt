# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy

from .Malt.PipelineTest import PipelineTest
from .Malt.Mesh import Mesh
from .Malt import GL
from .Malt import Scene

from . import MaltPipeline

from itertools import chain

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
    
    def load_mesh(self, mesh_object):
        mesh = mesh_object.to_mesh()
        #TODO: Blender indexes vertex positions and normals, but not uvs and colors,
        #we might need to do our own indexing or don't do indexing at all
        mesh.calc_loop_triangles()
        positions = [0]*len(mesh.vertices)*3
        mesh.vertices.foreach_get("co", positions)
        normals = [0]*len(mesh.vertices)*3
        mesh.vertices.foreach_get("normal", normals)
        indices = [0]*len(mesh.loop_triangles)*3
        mesh.loop_triangles.foreach_get("vertices", indices)

        self.meshes[mesh_object.name] = self.get_pipeline().load_mesh(positions, indices, normals)
    
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
        for obj in context.scene.objects:
            if obj.type == 'MESH':
                material = None
                slots = obj.material_slots 
                if len(slots) > 0 and slots[0].material:
                    malt = slots[0].material.malt
                    material = Scene.Material(malt.shader_source, malt.parameters)
                matrix = flatten_matrix(obj.matrix_world)
                scene.objects.append(Scene.Object(matrix, self.meshes[obj.name], material))
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
        if self.first_update:
            # First time initialization
            self.first_update = False
            # Loop over all datablocks used in the scene.
            for datablock in depsgraph.ids:
                if datablock.__class__  is bpy.types.Object and datablock.type == 'MESH':
                    self.load_mesh(datablock)
        else:
            # Test which datablocks changed
            for update in depsgraph.updates:
                if update.is_updated_geometry:
                    if update.id.__class__  is bpy.types.Object and update.id.type == 'MESH':
                        self.load_mesh(update.id)

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
