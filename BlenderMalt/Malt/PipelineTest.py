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

_obj_pixel_pre='''
#version 410 core

#define PIXEL_SHADER

#include "Common.glsl"

layout (location = 0) out vec4 OUT_COLOR;

#define MAIN_PASS void main()
'''

_obj_pixel_default= '''
MAIN_PASS
{
    OUT_COLOR = vec4(1,1,0,1);
}
'''


class PipelineTest(Pipeline):

    def __init__(self):
        super().__init__()

        self.parameters.world["Background Color"] = GLUniform(-1, GL_FLOAT_VEC4, (0.5,0.5,0.5,1))
        '''
        self.parameters.scene["test"] = GLUniform(-1, GL_FLOAT_VEC4, (1,1,0,1))
        self.parameters.world["test"] = GLUniform(-1, GL_FLOAT_VEC4, (1,1,0,1))
        self.parameters.object["test"] = GLUniform(-1, GL_FLOAT_VEC4, (1,1,0,1))
        self.parameters.light["test"] = GLUniform(-1, GL_FLOAT_VEC4, (1,1,0,1))
        '''

        self.resolution = None

        self.default_shader = self.compile_shader_from_source(_obj_pixel_default)

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
        pixel = shader_preprocessor(_obj_pixel_pre + shader_source, include_dirs)
        shader = Shader(vertex, pixel)
        return {
            'MAIN_PASS' : shader,
        }

    def compile_shader(self, shader_path):
        from os import path

        file_dir = path.dirname(shader_path)
        source = '#include "{}"'.format(shader_path)
        
        return self.compile_shader_from_source(source, [file_dir])
    
    def resize_render_targets(self, resolution):
        self.resolution = resolution
        w,h = self.resolution

        self.t_color = Texture((w,h), GL_RGB32F)
        self.t_depth = Texture((w,h), GL_DEPTH24_STENCIL8, GL_UNSIGNED_INT_24_8)
        self.fbo = RenderTarget([self.t_color], self.t_depth)
    
    def render(self, resolution, scene):
        if self.resolution != resolution:
            self.resize_render_targets(resolution)

        self.fbo.bind()

        glClearColor(*scene.world_parameters['Background Color'])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        glEnable(GL_DEPTH_TEST)
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

        self.common_UBO.load_data(self.common_data)
        
        for obj in scene.objects:
            shader = self.default_shader['MAIN_PASS']
            if obj.material and obj.material.shader['MAIN_PASS']:
                shader = obj.material.shader['MAIN_PASS']
            shader.uniforms['MODEL'].set_value(obj.matrix)
            #shader.uniforms['CAMERA'].set_value(scene.camera.camera_matrix)
            #shader.uniforms['PROJECTION'].set_value(scene.camera.projection_matrix)
            shader.bind()
            self.common_UBO.bind(shader.uniform_blocks['COMMON_UNIFORMS'])
            self.light_UBO.bind(shader.uniform_blocks['SCENE_LIGHTS'])
            obj.mesh.draw()

        return self.t_color
