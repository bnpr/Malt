from os import path

from Malt.GL.GL import *
from Malt.GL.Mesh import Mesh
from Malt.GL.RenderTarget import RenderTarget
from Malt.GL.Shader import Shader, UBO
from Malt.GL.Texture import Texture

from Malt.Render import Common
from Malt.Pipeline import *

class MiniPipeline(Pipeline):

    DEFAULT_SHADER = None

    def __init__(self, plugins=[]):
        super().__init__(plugins)

        self.parameters.world['Background Color'] = Parameter((0.5,0.5,0.5,1), Type.FLOAT, 4)

        self.common_buffer = Common.CommonBuffer()
        
        if MiniPipeline.DEFAULT_SHADER is None: 
            source = '''
            #include "Common.glsl"

            #ifdef VERTEX_SHADER
            void main()
            {
                DEFAULT_VERTEX_SHADER();
            }
            #endif

            #ifdef PIXEL_SHADER
            layout (location = 0) out vec4 RESULT;
            void main()
            {
                PIXEL_SETUP_INPUT();
                RESULT = vec4(1);
            }
            #endif
            '''
            MiniPipeline.DEFAULT_SHADER = self.compile_material_from_source('mesh', source)
        
        self.default_shader = MiniPipeline.DEFAULT_SHADER
        
    def compile_material_from_source(self, material_type, source, include_paths=[]):
        return {
            'MAIN_PASS' : self.compile_shader_from_source(
                source, include_paths, ['MAIN_PASS']
            )
        }
    
    def setup_render_targets(self, resolution):
        self.t_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        self.t_main_color = Texture(resolution, GL_RGBA32F)
        self.fbo_main = RenderTarget([self.t_main_color], self.t_depth)
        
    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        self.common_buffer.load(scene, resolution)
        
        shader_resources = { 'COMMON_UNIFORMS' : self.common_buffer }

        self.fbo_main.clear([scene.world_parameters['Background Color']], 1)

        self.draw_scene_pass(self.fbo_main, scene.batches, 'MAIN_PASS', self.default_shader['MAIN_PASS'], shader_resources)

        return { 'COLOR' : self.t_main_color }


PIPELINE = MiniPipeline
    