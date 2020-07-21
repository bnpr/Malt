# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

from .GL import *
from .Pipeline import Pipeline
from .Mesh import Mesh
from .Shader import Shader
from .Texture import Texture
from .RenderTarget import RenderTarget
from .Parameter import Parameter
from .UBO import UBO

from .Render import Lighting
from .Render import Common

_obj_vertex_default='''
#version 410 core

#define VERTEX_SHADER

#include "Common.glsl"
'''

_obj_pixel_prepass='''
#version 410 core

#define PIXEL_SHADER

#include "Common.glsl"

layout (location = 0) out vec4 OUT_NORMAL_DEPTH;
//layout (location = 1) out float OUT_DEPTH;
layout (location = 1) out unsigned int OUT_ID;

uniform unsigned int ID;

void main()
{
    OUT_NORMAL_DEPTH.rgb = normalize(NORMAL);
    OUT_NORMAL_DEPTH.a = -transform_point(CAMERA, POSITION).z;
    OUT_ID = ID;
}
'''

_obj_pixel_pre='''
#version 410 core

#define PIXEL_SHADER

#include "Common.glsl"

layout (location = 0) out vec4 OUT_COLOR;

uniform unsigned int ID;
uniform sampler2D IN_NORMAL_DEPTH;
uniform usampler2D IN_ID;

#define MAIN_PASS void main()
'''

_obj_pixel_default= _obj_pixel_pre + '''
MAIN_PASS
{
    OUT_COLOR = vec4(1,1,0,1);
}
'''

_obj_pixel_composite_depth= _obj_pixel_pre + '''

layout (location = 1) out float OUT_DEPTH;

MAIN_PASS
{
    OUT_DEPTH = -transform_point(CAMERA, POSITION).z;
}
'''


class PipelineTest(Pipeline):

    def __init__(self):
        super().__init__()

        self.parameters.world["Background Color"] = GLUniform(-1, GL_FLOAT_VEC4, (0.5,0.5,0.5,1))

        self.resolution = None

        self.default_shader = self.compile_shader_from_source(_obj_pixel_default)
        self.composite_depth_shader = self.compile_shader_from_source(_obj_pixel_composite_depth)

        self.prepass_shader = self.compile_shader_from_source(_obj_pixel_prepass)
        print(self.prepass_shader.uniforms)
        
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

        self.common_data = Common.CommonBuffer()
        self.common_UBO = UBO()
        
        self.light_data = Lighting.LightsBuffer()
        self.light_UBO = UBO()

    def compile_shader_from_source(self, shader_source, include_dirs=[]):
        from os import path

        shader_dir = path.join(path.dirname(__file__), "Render", "Shaders")
        include_dirs.append(shader_dir)
        
        vertex = shader_preprocessor(_obj_vertex_default, include_dirs)
        pixel = shader_preprocessor(shader_source, include_dirs)
        shader = Shader(vertex, pixel)
        return shader

    def compile_shader(self, shader_path):
        from os import path

        file_dir = path.dirname(shader_path)
        source = _obj_pixel_pre + '#include "{}"'.format(shader_path)
        
        return {
            'MAIN_PASS' : self.compile_shader_from_source(source, [file_dir])
        }
    
    def resize_render_targets(self, resolution):
        self.resolution = resolution
        w,h = self.resolution

        self.t_depth = Texture((w,h), GL_DEPTH_COMPONENT32F)
        
        self.t_prepass_normal_depth = Texture((w,h), GL_RGBA32F)
        self.t_prepass_id = Texture((w,h), GL_R32UI, GL_INT)
        self.fbo_prepass = RenderTarget([self.t_prepass_normal_depth, self.t_prepass_id], self.t_depth)
        
        self.t_color = Texture((w,h), GL_RGB32F)
        self.fbo = RenderTarget([self.t_color], self.t_depth)
        
        self.t_composite_depth = Texture((w,h), GL_R32F)
        self.fbo_composite_depth = RenderTarget([None, self.t_composite_depth], self.t_depth)
    
    def render(self, resolution, scene, is_final_render):
        if self.resolution != resolution:
            self.resize_render_targets(resolution)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        for i, light in enumerate(scene.lights):
            self.light_data.lights[i].color = light.color
            self.light_data.lights[i].type = light.type
            self.light_data.lights[i].position = light.position
            self.light_data.lights[i].radius = light.radius
            self.light_data.lights[i].direction = light.direction
            self.light_data.lights[i].spot_angle = light.spot_angle
            self.light_data.lights[i].spot_blend = light.spot_blend
        self.light_data.lights_count = len(scene.lights)
        
        self.light_UBO.load_data(self.light_data)

        self.common_data.CAMERA = tuple(scene.camera.camera_matrix)
        self.common_data.PROJECTION = tuple(scene.camera.projection_matrix)
        self.common_data.RESOLUTION = resolution

        self.common_UBO.load_data(self.common_data)

        self.fbo_prepass.bind()
        glClearColor(0,0,0,0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        shader = self.prepass_shader
        print(shader.vertex_source)
        print(shader.error)
        for i, obj in enumerate(scene.objects):
            shader.uniforms['MODEL'].set_value(obj.matrix)
            shader.uniforms['ID'].set_value(i)
            shader.bind()
            self.common_UBO.bind(shader.uniform_blocks['COMMON_UNIFORMS'])
            obj.mesh.draw()

        self.fbo.bind()
        glClearColor(*scene.world_parameters['Background Color'])
        glClear(GL_COLOR_BUFFER_BIT)
        
        for i, obj in enumerate(scene.objects):
            shader = self.default_shader
            if obj.material and obj.material.shader['MAIN_PASS']:
                shader = obj.material.shader['MAIN_PASS']
            shader.uniforms['MODEL'].set_value(obj.matrix)
            if 'ID' in shader.uniforms: 
                shader.uniforms['ID'].set_value(i)
            if 'IN_NORMAL_DEPTH' in shader.textures: 
                shader.textures['IN_NORMAL_DEPTH'] = self.t_prepass_normal_depth
            if 'IN_ID' in shader.textures: 
                shader.textures['IN_ID'] = self.t_prepass_id
            shader.bind()
            self.common_UBO.bind(shader.uniform_blocks['COMMON_UNIFORMS'])
            self.light_UBO.bind(shader.uniform_blocks['SCENE_LIGHTS'])
            obj.mesh.draw()

        if is_final_render:

            glDisable(GL_DEPTH_TEST)

            self.fbo_composite_depth.bind()
            
            glClearColor(10.0e+32,1.0,1.0,1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            shader = self.composite_depth_shader
            self.common_UBO.bind(shader.uniform_blocks['COMMON_UNIFORMS'])
            
            for obj in scene.objects:
                shader.uniforms['MODEL'].set_value(obj.matrix)
                shader.bind()
                obj.mesh.draw()

        return {
            'COLOR' : self.t_color,
            'DEPTH' : self.t_composite_depth,
        }
        
