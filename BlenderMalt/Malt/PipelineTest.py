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
from .Render import Sampling


_obj_vertex_default='''
#version 410 core
#extension GL_ARB_shading_language_include : enable

#define VERTEX_SHADER
#define DEFAULT_VERTEX_SHADER

#include "Common.glsl"
'''

_obj_pixel_prepass='''
#version 410 core
#extension GL_ARB_shading_language_include : enable

#define PIXEL_SHADER

#include "Common.glsl"

layout (location = 0) out vec4 OUT_NORMAL_DEPTH;
layout (location = 1) out uint OUT_ID;

uniform uint ID;

void main()
{
    OUT_NORMAL_DEPTH.rgb = normalize(NORMAL);
    OUT_NORMAL_DEPTH.a = gl_FragCoord.z;
    OUT_ID = ID;
}
'''

_obj_pixel_pre='''
#version 410 core
#extension GL_ARB_shading_language_include : enable

#define PIXEL_SHADER
#include "Common.glsl"

layout (location = 0) out vec4 OUT_COLOR;

uniform uint ID;
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

_obj_pixel_composite_depth='''
#version 410 core
#extension GL_ARB_shading_language_include : enable

#define PIXEL_SHADER
#include "Common.glsl"

layout (location = 0) out float OUT_DEPTH;

void main()
{
    OUT_DEPTH = -transform_point(CAMERA, POSITION).z;
}
'''

class PipelineTest(Pipeline):

    def __init__(self):
        super().__init__()

        self.sampling_grid_size = 2

        self.parameters.scene['Preview Samples'] = GLUniform(-1, GL.GL_INT, 4)
        self.parameters.scene['Render Samples'] = GLUniform(-1, GL.GL_INT, 8)
        self.parameters.world['Background Color'] = GLUniform(-1, GL_FLOAT_VEC4, (0.5,0.5,0.5,1))

        self.default_shader = self.compile_shader_from_source(_obj_pixel_default)
        self.composite_depth_shader = self.compile_shader_from_source(_obj_pixel_composite_depth)
        self.prepass_shader = self.compile_shader_from_source(_obj_pixel_prepass)

        self.common_buffer = Common.CommonBuffer()
        self.lights_buffer = Lighting.LightsBuffer()

    def compile_shader_from_source(self, shader_source, include_dirs=[]):
        from os import path

        shader_dir = path.join(path.dirname(__file__), 'Render', 'Shaders')
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
    
    def setup_render_targets(self, resolution):
        self.t_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        
        self.t_prepass_normal_depth = Texture(resolution, GL_RGBA32F)
        self.t_prepass_id = Texture(resolution, GL_R32UI, GL_INT)
        self.fbo_prepass = RenderTarget([self.t_prepass_normal_depth, self.t_prepass_id], self.t_depth)
        
        self.t_color = Texture(resolution, GL_RGB32F)
        self.fbo = RenderTarget([self.t_color], self.t_depth)

        self.t_color_accumulate = Texture(resolution, GL_RGB32F)
        self.fbo_accumulate = RenderTarget([self.t_color_accumulate])
        
        self.t_composite_depth = Texture(resolution, GL_R32F)
        self.fbo_composite_depth = RenderTarget([self.t_composite_depth], self.t_depth)
    
    def get_samples(self):
        return Sampling.get_RGSS_samples(self.sampling_grid_size)
    
    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        #SETUP SAMPLING
        if is_final_render:
            self.sampling_grid_size = scene.parameters['Render Samples'][0]
        else:
            self.sampling_grid_size = scene.parameters['Preview Samples'][0]

        sample_offset = self.get_samples()[self.sample_count]

        #SETUP UNIFORM BLOCKS
        self.common_buffer.load(scene, resolution, sample_offset, self.sample_count)
        self.lights_buffer.load(scene)
        UBOS = {
            'COMMON_UNIFORMS' : self.common_buffer,
            'SCENE_LIGHTS' : self.lights_buffer
        }
        
        #SETUP PER-OBJECT PARAMETERS
        for i, obj in enumerate(scene.objects):
            obj.parameters['MODEL'] = obj.matrix
            obj.parameters['ID'] = i+1

        #PRE-PASS
        self.fbo_prepass.clear((0,0,1,1),1,0)
        self.draw_scene_pass(self.fbo_prepass, scene.objects, None, self.prepass_shader, UBOS)

        #MAIN-PASS
        textures = {
            'IN_NORMAL_DEPTH': self.t_prepass_normal_depth,
            'IN_ID': self.t_prepass_id,
        }
        self.fbo.clear(scene.world_parameters['Background Color'])
        self.draw_scene_pass(self.fbo, scene.objects, 'MAIN_PASS', self.default_shader, UBOS, {}, textures)        
        
        # TEMPORAL SUPER-SAMPLING ACCUMULATION
        # TODO: Should accumulate in display space 
        # https://therealmjp.github.io/posts/msaa-overview/#working-with-hdr-and-tone-mapping
        self.blend_texture(self.t_color, self.fbo_accumulate, 1.0 / (self.sample_count + 1))

        #COMPOSITE DEPTH
        if is_final_render:
            self.fbo_composite_depth.clear((10.0e+32,1.0,1.0,1.0))
            self.draw_scene_pass(self.fbo_composite_depth, scene.objects, None, self.composite_depth_shader, UBOS)

        return {
            'COLOR' : self.t_color_accumulate,
            'DEPTH' : self.t_composite_depth,
        }

