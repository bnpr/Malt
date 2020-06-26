# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from .GL import *
from .Pipeline import Pipeline
from .Mesh import Mesh
from .Shader import Shader
from .Texture import Texture
from .RenderTarget import RenderTarget

_vertex = '''
#version 330 core
layout (location = 0) in vec4 vertex_position;

uniform vec2 scale = vec2(1,1);

out vec4 position;

void main()
{
    position = vertex_position;
    position = vec4(position.xy * scale,0.5,1);
    gl_Position = position;
}
'''

_pixel = '''
#version 330 core
layout (location = 0) out vec4 color_A;
layout (location = 1) out vec4 color_B;
in vec4 position;

uniform vec4 color = vec4(1,1,0,1);

void main()
{
    vec2 uv = (position.xy + vec2(1,1)) / 2.0;
    color_A = color;
    color_B = color;
}
'''

_pixel_texture='''
#version 450 core
in vec4 position;

layout(binding=0) uniform sampler2D color;

void main()
{
    vec2 uv = (position.xy + vec2(1,1)) / 2.0;
    gl_FragColor = texture(color, position.xy);
}
'''

_obj_vertex='''
#version 450 core
layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_uv0;
layout (location = 3) in vec2 in_uv1;
layout (location = 4) in vec2 in_uv2;
layout (location = 5) in vec2 in_uv3;
layout (location = 10) in vec4 in_color0;
layout (location = 11) in vec4 in_color1;
layout (location = 12) in vec4 in_color2;
layout (location = 13) in vec4 in_color3;

uniform mat4 _projection;
uniform mat4 _camera;
uniform mat4 _model;

out vec3 position;
out vec3 normal;
out vec2 uv[4];
out vec4 color[4];

void main()
{
    position = (_model * vec4(in_position,1)).xyz;
    normal = normalize(mat3(_model) * in_normal);

    uv[0]=in_uv0;
    uv[1]=in_uv1;
    uv[2]=in_uv2;
    uv[3]=in_uv3;

    color[0]=in_color0;
    color[1]=in_color1;
    color[2]=in_color2;
    color[3]=in_color3;

    gl_Position = _projection * _camera * vec4(position,1);
}
'''

_obj_pixel='''
#version 450 core

uniform mat4 _projection;
uniform mat4 _camera;
uniform mat4 _model;

in vec3 position;
in vec3 normal;
in vec2 uv[4];
in vec4 color[4];

layout (location = 0) out vec4 COLOR;

void main()
{
    COLOR = vec4(1,1,0,1);
    //float n_dot = dot(vec3(0,0,1), normal);
    //color.b = n_dot;
}
'''

_obj_pixel_pre='''
#version 450 core

uniform mat4 _projection;
uniform mat4 _camera;
uniform mat4 _model;

in vec3 position;
in vec3 normal;
in vec2 uv[4];
in vec4 color[4];

layout (location = 0) out vec4 COLOR;

#define MAIN_PASS void main()
'''

class PipelineTest(Pipeline):

    def __init__(self):
        super().__init__()
        
        self.resolution = None

        self.obj_shader = Shader(_obj_vertex, _obj_pixel)

        self.shader = Shader(_vertex, _pixel)
        self.texture_shader = Shader(_vertex, _pixel_texture)

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

    def compile_shader(self, shader_path):
        shader_source = load_preprocessed_file(shader_path)
        vertex = _obj_vertex
        pixel = _obj_pixel_pre + shader_source
        shader = Shader(vertex, pixel)
        return {
            'MAIN_PASS' : shader,
        }
    
    def resize_render_targets(self, resolution):
        self.resolution = resolution
        w,h = self.resolution

        self.t_color = Texture((w,h))
        self.t_color_b = Texture((w,h))
        self.t_depth = Texture((w,h), GL_DEPTH24_STENCIL8, GL_UNSIGNED_INT_24_8)
        self.fbo = RenderTarget([self.t_color, self.t_color_b], self.t_depth)
    
    def render(self, resolution, scene):
        if self.resolution != resolution:
            self.resize_render_targets(resolution)

        self.fbo.bind()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        self.shader.bind()
        self.shader.uniforms['color'].set_value([0.5,0.5,0.5,1.0])
        self.shader.uniforms['color'].bind()
        self.quad.draw()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        for obj in scene.objects:
            shader = self.obj_shader
            if obj.material and obj.material.shader['MAIN_PASS']:
                shader = obj.material.shader['MAIN_PASS']
            shader.uniforms['_projection'].set_value(scene.camera.projection_matrix)
            shader.uniforms['_camera'].set_value(scene.camera.camera_matrix)
            shader.uniforms['_model'].set_value(obj.matrix)
            shader.bind()
            obj.mesh.draw()

        return self.t_color
