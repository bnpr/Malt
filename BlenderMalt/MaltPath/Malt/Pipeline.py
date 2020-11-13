# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from os import path
import ctypes

from Malt.GL import *
from Malt.Shader import Shader
from Malt.Parameter import *
from Malt.UBO import UBO
from Malt.Mesh import Mesh

_screen_vertex_default='''
#version 410 core

layout (location = 0) in vec3 in_position;
out vec3 POSITION;
out vec2 UV;

void main()
{
    POSITION = in_position;
    UV = in_position.xy * 0.5 + 0.5;

    gl_Position = vec4(POSITION, 1);
}
'''

_screen_pixel_blend='''
#version 410 core

in vec3 POSITION;
in vec2 UV;

uniform sampler2D blend_texture;
uniform float opacity = 1.0;

layout (location = 0) out vec4 OUT_COLOR;

void main()
{
    vec4 color = texture(blend_texture, UV);
    OUT_COLOR = vec4(color.xyz, opacity);
    //TODO: This should be :
    //OUT_COLOR = vec4(color.xyz, color.a * opacity);
}
'''

_BLEND_SHADER = None

class Pipeline(object):

    SHADER_INCLUDE_PATHS = []

    def __init__(self):
        self.parameters = PipelineParameters()
        self.parameters.mesh['double_sided'] = Parameter(False, Type.BOOL)
        self.parameters.mesh['precomputed_tangents'] = Parameter(False, Type.BOOL)

        shader_dir = path.join(path.dirname(__file__), 'Render', 'Shaders')
        if shader_dir not in Pipeline.SHADER_INCLUDE_PATHS:
            Pipeline.SHADER_INCLUDE_PATHS.append(shader_dir)

        self.resolution = None
        self.sample_count = 0

        self.result = None

        positions=[
             1.0,  1.0, 0.0,
             1.0, -1.0, 0.0,
            -1.0, -1.0, 0.0,
            -1.0,  1.0, 0.0,
        ]
        indices=[
            0, 1, 3,
            1, 2, 3,
        ]
        
        self.quad = Mesh(positions, indices)
        global _BLEND_SHADER
        if _BLEND_SHADER is None: _BLEND_SHADER = Shader(_screen_vertex_default, _screen_pixel_blend)
        self.blend_shader = _BLEND_SHADER
        
        self.default_shader = None
    
    def setup_render_targets(self, resolution):
        pass

    def draw_screen_pass(self, shader, target, blend = False):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        if blend:
            glEnable(GL_BLEND)
        else:
            glDisable(GL_BLEND)
        target.bind()
        shader.bind()
        self.quad.draw()
    
    def blend_texture(self, blend_texture, target, opacity):
        self.blend_shader.textures['blend_texture'] = blend_texture
        self.blend_shader.uniforms['opacity'].set_value(opacity)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.draw_screen_pass(self.blend_shader, target, True)
    
    def draw_scene_pass(self, render_target, objects, pass_name=None, default_shader=None, uniform_blocks={}, uniforms={}, textures={}, shader_callbacks=[]):
        batches = self.batches
        
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        render_target.bind()

        for material, meshes in batches.items():
            shader = default_shader
            if material and pass_name in material.shader and material.shader[pass_name]:
                shader = material.shader[pass_name]
            
            for name, uniform in uniforms.items():
                if name in shader.uniforms:
                    shader.uniforms[name].set_value(uniform)
            
            for name, texture in textures.items():
                if name in shader.textures:
                    shader.textures[name] = texture
            
            for callback in shader_callbacks:
                callback(shader)
            
            shader.bind()

            for name, block in uniform_blocks.items():
                if name in shader.uniform_blocks:
                    block.bind(shader.uniform_blocks[name])

            for mesh, batches in meshes.items():

                if mesh.parameters['double_sided']:
                    glDisable(GL_CULL_FACE)
                else:
                    glEnable(GL_CULL_FACE)
                    glCullFace(GL_BACK)
                
                mesh.mesh.bind()
                
                for batch in batches:
                    batch['BATCH_MODELS'].bind(shader.uniform_blocks['BATCH_MODELS'])
                    batch['BATCH_IDS'].bind(shader.uniform_blocks['BATCH_IDS'])
                    glDrawElementsInstanced(GL_TRIANGLES, mesh.mesh.index_count, GL_UNSIGNED_INT, NULL, batch['instances_count'])
        
        '''
        last_double_sided = None
        last_neg_scale = None
        last_shader = None
        last_mesh = None

        for obj in objects:
            
            double_sided = obj.mesh.parameters['double_sided']
            if double_sided != last_double_sided:
                if obj.mesh.parameters['double_sided']:
                    glDisable(GL_CULL_FACE)
                else:
                    glEnable(GL_CULL_FACE)
                    glCullFace(GL_BACK)
            
            if obj.negative_scale != last_neg_scale:
                if obj.negative_scale:
                    glFrontFace(GL_CW)
                else:
                    glFrontFace(GL_CCW)

            shader = default_shader
            if obj.material and pass_name in obj.material.shader and obj.material.shader[pass_name]:
                shader = obj.material.shader[pass_name]
            
            if shader != last_shader:
                for name, uniform in uniforms.items():
                    if name in shader.uniforms:
                        shader.uniforms[name].set_value(uniform)
                
                for name, texture in textures.items():
                    if name in shader.textures:
                        shader.textures[name] = texture
                
                for callback in shader_callbacks:
                    callback(shader)
                
                shader.bind()

                #TODO: Do the opposite. Set the shader uniform block location to the UBO location
                for name, block in uniform_blocks.items():
                    if name in shader.uniform_blocks:
                        block.bind(shader.uniform_blocks[name])
            
            shader.uniforms['MODEL'].bind(obj.matrix)
            if shader != last_shader or obj.negative_scale != last_neg_scale:
                shader.uniforms['MIRROR_SCALE'].bind(obj.negative_scale)
            
            for key, value in obj.parameters:
                if key in shader.uniforms:
                    shader.uniforms[key].bind(value)
            
            if obj.mesh is not last_mesh:
                obj.mesh.mesh.bind()
            obj.mesh.mesh.draw(False)

            last_double_sided = double_sided
            last_neg_scale = obj.negative_scale
            last_shader = shader
            last_mesh = obj.mesh
        '''


    def get_parameters(self):
        return self.parameters
    
    def get_samples(self):
        return [(0,0)]
    
    def needs_more_samples(self):
        return self.sample_count < len(self.get_samples())
    
    def compile_shader_from_source(self, shader_source, vertex_pass=None, pixel_pass=None, include_paths=[], defines=[]):
        include_paths.extend(Pipeline.SHADER_INCLUDE_PATHS)
        
        #TODO: auto-define the pass name
        vertex = shader_preprocessor(shader_source, include_paths, ['VERTEX_SHADER'] + defines, vertex_pass)
        pixel = shader_preprocessor(shader_source, include_paths, ['PIXEL_SHADER'] + defines, pixel_pass)

        return Shader(vertex, pixel)
    
    def compile_shader(self, shader_path):
        file_dir = path.dirname(shader_path)
        source = open(shader_path).read()
        return self.compile_shader_from_source(source, include_paths=[file_dir])
    
    def compile_material_from_source(self, material_type, source, include_paths=[]):
        return {}
    
    def compile_material(self, shader_path):
        file_dir = path.dirname(shader_path)
        material_type = shader_path.split('.')[-2]
        source = '#include "{}"'.format(shader_path)
        return self.compile_material_from_source(material_type, source, [file_dir])

    def render(self, resolution, scene, is_final_render, is_new_frame):
        if self.resolution != resolution:
            self.resolution = resolution
            self.setup_render_targets(resolution)
            self.sample_count = 0
        
        if is_new_frame:
            self.sample_count = 0
        
        if self.needs_more_samples() == False:
            return self.result
        
        scene.objects.sort(key = lambda e: (id(e.material), id(e.mesh)))
        
        self.result = self.do_render(resolution, scene, is_final_render, is_new_frame)
        
        self.sample_count += 1

        return self.result

    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        return {}

