# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from .Mesh import Mesh
from .Shader import Shader
from .GL import *

class PipelineParameters(object):

    def __init__(self, scene={}, world={}, camera={}, object={}, material={}, light={}):
        self.scene = scene
        self.world = world
        self.camera = camera
        self.object = object
        self.material = material
        self.light = light

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
    OUT_COLOR = texture(blend_texture, UV) * opacity;
}
'''

class Pipeline(object):

    def __init__(self):
        self.parameters = PipelineParameters()

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
        self.blend_shader = Shader(_screen_vertex_default, _screen_pixel_blend)
    
    def setup_render_targets(self, resolution):
        pass

    def draw_screen_pass(self, shader, target):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        target.bind()
        shader.bind()
        self.quad.draw()
    
    def blend_texture(self, blend_texture, target, opacity):
        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
        self.blend_shader.textures['blend_texture'] = blend_texture
        self.blend_shader.uniforms['opacity'].set_value(opacity)
        self.draw_screen_pass(self.blend_shader, target)
    
    def draw_scene_pass(self, render_target, objects, pass_name=None, default_shader=None, uniform_blocks={}, uniforms={}, textures={}):
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_CULL_FACE)

        render_target.bind()

        for obj in objects:
            if obj.negative_scale:
                glCullFace(GL_FRONT)
            else:
                glCullFace(GL_BACK)

            shader = default_shader
            if obj.material and pass_name in obj.material.shader:
                shader = obj.material.shader[pass_name]
            
            for name, uniform in uniforms.items():
                if name in shader.uniforms:
                    shader.uniforms[name].set_value(uniform)
            
            #per object parameters and overrides
            for name, param in obj.parameters.items():
                if name in shader.uniforms:
                    shader.uniforms[name].set_value(param)
            
            for name, texture in textures.items():
                if name in shader.textures:
                    shader.textures[name] = texture
            
            shader.bind()

            for name, block in uniform_blocks.items():
                if name in default_shader.uniform_blocks:
                    block.bind(default_shader.uniform_blocks[name])
            
            obj.mesh.draw()

    def get_parameters(self):
        return self.parameters
    
    def get_samples(self):
        return [(0,0)]
    
    def needs_more_samples(self):
        return self.sample_count < len(self.get_samples())
    
    def compile_shader(self, shader_path):
        return {
            'uniforms':{}, 
            'error':None,
        }

    def render(self, resolution, scene, is_final_render, is_new_frame):
        if self.resolution != resolution:
            self.resolution = resolution
            self.setup_render_targets(resolution)
            self.sample_count = 0
        
        if is_new_frame:
            self.sample_count = 0
        
        if self.needs_more_samples() == False:
            return self.result
        
        self.result = self.do_render(resolution, scene, is_final_render, is_new_frame)
        
        self.sample_count += 1

        return self.result


    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        return {}

