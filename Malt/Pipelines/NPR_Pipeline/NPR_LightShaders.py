
from Malt.GL.GL import *
from Malt.GL.Shader import UBO
from Malt.GL.Texture import TextureArray
from Malt.GL.RenderTarget import ArrayLayerTarget, RenderTarget

from Malt.Render import Lighting

from Malt.PipelineParameters import MaterialParameter
from Malt.PipelineGraph import *

import ctypes


class NPR_LightShaders():

    def __init__(self, parameters):
        parameters.light['Shader'] = MaterialParameter('', '.light.glsl')

        class C_NPR_LightShadersBuffer(ctypes.Structure):
            _fields_ = [
                ('custom_shading_index', ctypes.c_int*Lighting.MAX_LIGHTS),
            ]
        self.data = C_NPR_LightShadersBuffer()
        self.custom_shading_count = 0
        self.UBO = UBO()

        self.texture = None
        self.fbos = None
    
    @classmethod
    def setup_graphs(self, pipeline, graphs):
        from Malt.Pipelines.NPR_Pipeline.NPR_Pipeline import _COMMON_HEADER
        graphs['Light'] = GLSLPipelineGraph(
            name='Light',
            graph_type=GLSLPipelineGraph.INTERNAL_GRAPH,
            default_global_scope=_COMMON_HEADER,
            graph_io=[ 
                GLSLGraphIO(
                    name='LIGHT_SHADER',
                    shader_type='PIXEL_SHADER',
                )
            ]
        )
        graphs['Light'].setup_reflection(pipeline, "void LIGHT_SHADER(LightShaderInput I, inout LightShaderOutput O) { }")
    
    def load(self, pipeline, depth_texture, scene, lights_buffer):
        self.custom_shading_count = 0
        for i, light in enumerate(scene.lights):
            custom_shading_index = -1
            if light.parameters['Shader'] is not None:
                custom_shading_index = self.custom_shading_count
                self.custom_shading_count += 1
            self.data.custom_shading_index[i] = custom_shading_index

        self.UBO.load_data(self.data)

        if self.custom_shading_count == 0:
            return

        lights = [l for l in scene.lights if l.parameters['Shader'] is not None]
        tex = self.texture
        if tex is None or tex.resolution != depth_texture.resolution or tex.length < len(lights):
            self.texture = TextureArray(depth_texture.resolution, len(lights), GL_RGB32F)
            self.fbos = []
            for i in range(len(lights)):
                self.fbos.append(RenderTarget([ArrayLayerTarget(self.texture, i)]))
        
        for i, light in enumerate(lights):
            material = light.parameters['Shader']
            if material.shader and 'SHADER' in material.shader.keys():
                shader = material.shader['SHADER']
                pipeline.common_buffer.bind(shader.uniform_blocks['COMMON_UNIFORMS'])
                lights_buffer.bind(shader.uniform_blocks['SCENE_LIGHTS'])
                shader.textures['IN_DEPTH'] = depth_texture
                if 'LIGHT_INDEX' in shader.uniforms:
                    light_index = scene.lights.index(light)
                    shader.uniforms['LIGHT_INDEX'].set_value(light_index)
                pipeline.draw_screen_pass(shader, self.fbos[i])
    
    def shader_callback(self, shader):
        if 'LIGHTS_CUSTOM_SHADING' in shader.uniform_blocks:
            self.UBO.bind(shader.uniform_blocks['LIGHTS_CUSTOM_SHADING'])
        shader.textures['IN_LIGHT_CUSTOM_SHADING'] = self.texture


