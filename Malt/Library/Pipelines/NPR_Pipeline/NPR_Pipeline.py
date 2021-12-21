# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

from os import path

from Malt.Pipeline import *
from Malt.PipelineGraph import *
from Malt.PipelineNode import PipelineNode

from Malt.GL.GL import *
from Malt.GL.RenderTarget import RenderTarget
from Malt.GL.Texture import Texture
from Malt.GL.Texture import internal_format_to_vector_type, internal_format_to_sampler_type, internal_format_to_data_format

from Malt.Library.Render import Common
from Malt.Library.Render import DepthToCompositeDepth
from Malt.Library.Render import Sampling

from Malt.Library.Pipelines.NPR_Pipeline.NPR_Lighting import NPR_Lighting
from Malt.Library.Pipelines.NPR_Pipeline.NPR_LightShaders import NPR_LightShaders

from Malt.Library.Nodes import Unpack8bitTextures

from Malt.Library.Pipelines.NPR_Pipeline.Nodes import ScreenPass, PrePass, MainPass

_COMMON_HEADER = '''
#include "NPR_Pipeline.glsl"
#include "Node Utils/node_utils.glsl"
'''

_SCREEN_SHADER_HEADER= _COMMON_HEADER + '''
#ifdef PIXEL_SHADER
void SCREEN_SHADER(vec2 uv);
void main(){ PIXEL_SETUP_INPUT(); SCREEN_SHADER(UV[0]); }
#endif //PIXEL_SHADER
'''

_DEFAULT_SHADER = None

_DEFAULT_SHADER_SRC='''
#include "NPR_Pipeline.glsl"

void PRE_PASS_PIXEL_SHADER(inout PrePassOutput PO){ }

void MAIN_PASS_PIXEL_SHADER() { }
'''

_BLEND_TRANSPARENCY_SHADER = None

_BLEND_TRANSPARENCY_SHADER_SRC='''
#include "Passes/BlendTransparency.glsl"
'''

class NPR_Pipeline(Pipeline):

    def __init__(self):
        super().__init__()

        shader_dir = path.join(path.dirname(__file__), 'Shaders')
        if shader_dir not in self.SHADER_INCLUDE_PATHS:
            self.SHADER_INCLUDE_PATHS.append(shader_dir)

        self.sampling_grid_size = 2
        self.samples = None

        self.parameters.world['Background.Color'] = Parameter((0.5,0.5,0.5,1), Type.FLOAT, 4)
        
        self.parameters.world['Samples.Grid Size'] = Parameter(8, Type.INT)
        self.parameters.world['Samples.Grid Size @ Preview'] = Parameter(4, Type.INT)
        self.parameters.world['Samples.Width'] = Parameter(1.5, Type.FLOAT)
        
        self.parameters.world['Transparency.Layers'] = Parameter(4, Type.INT)
        self.parameters.world['Transparency.Layers @ Preview'] = Parameter(1, Type.INT)
        
        default_material_path = os.path.join(os.path.dirname(__file__), 'default.mesh.glsl')
        self.parameters.world['Material.Default'] = MaterialParameter(default_material_path, '.mesh.glsl')
        
        self.parameters.world['Render Layer'] = Parameter('Render Layer', Type.GRAPH)
        self.render_layer_nodes = {}

        self.common_buffer = Common.CommonBuffer()
        self.npr_lighting = NPR_Lighting(self.parameters)
        self.npr_light_shaders = NPR_LightShaders(self.parameters)
        
        self.composite_depth = DepthToCompositeDepth.CompositeDepth()

        self.layer_query = DrawQuery()
        
        self.setup_graphs()
        
        global _DEFAULT_SHADER
        if _DEFAULT_SHADER is None: _DEFAULT_SHADER = self.compile_material_from_source('Mesh', _DEFAULT_SHADER_SRC)
        self.default_shader = _DEFAULT_SHADER

        global _BLEND_TRANSPARENCY_SHADER
        if _BLEND_TRANSPARENCY_SHADER is None: _BLEND_TRANSPARENCY_SHADER = self.compile_shader_from_source(_BLEND_TRANSPARENCY_SHADER_SRC)
        self.blend_transparency_shader = _BLEND_TRANSPARENCY_SHADER

    def get_mesh_shader_custom_outputs(self):
        return {
            'Line Color' : GL_RGBA16F,
            'Line Width' : GL_R16F,
        }
    
    def get_render_layer_custom_outputs(self):
        return {}
    
    def get_render_outputs(self):
        return super().get_render_outputs() | self.get_render_layer_custom_outputs()
    
    def get_samples(self, width=1.0):
        if self.samples is None:
            self.samples = Sampling.get_RGSS_samples(self.sampling_grid_size, width)
        return self.samples
    
    def setup_graphs(self):
        mesh = GLSLPipelineGraph(
            name='Mesh',
            graph_type=GLSLPipelineGraph.SCENE_GRAPH,
            default_global_scope=_COMMON_HEADER,
            shaders=['PRE_PASS', 'MAIN_PASS', 'SHADOW_PASS'],
            graph_io=[
                GLSLGraphIO(
                    name='PRE_PASS_PIXEL_SHADER',
                    define='CUSTOM_PRE_PASS',
                    shader_type='PIXEL_SHADER',
                    dynamic_output_types=GLSLGraphIO.COMMON_OUTPUT_TYPES,
                    custom_output_start_index=2,
                ),
                GLSLGraphIO(
                    name='MAIN_PASS_PIXEL_SHADER',
                    shader_type='MAIN_PASS',
                    dynamic_input_types=GLSLGraphIO.COMMON_INPUT_TYPES,
                    dynamic_output_types=GLSLGraphIO.COMMON_OUTPUT_TYPES,
                ),
                GLSLGraphIO(
                    name='VERTEX_DISPLACEMENT_SHADER',
                    define='CUSTOM_VERTEX_DISPLACEMENT',
                    shader_type='VERTEX_SHADER'
                ),
                GLSLGraphIO(
                    name='COMMON_VERTEX_SHADER',
                    define='CUSTOM_VERTEX_SHADER',
                    shader_type='VERTEX_SHADER',
                ),
            ]
        )
        mesh.setup_reflection(self, _DEFAULT_SHADER_SRC)

        screen = GLSLPipelineGraph(
            name='Screen',
            graph_type=GLSLPipelineGraph.GLOBAL_GRAPH,
            default_global_scope=_SCREEN_SHADER_HEADER,
            graph_io=[ 
                GLSLGraphIO(
                    name='SCREEN_SHADER',
                    dynamic_input_types= GLSLGraphIO.COMMON_INPUT_TYPES,
                    dynamic_output_types= GLSLGraphIO.COMMON_OUTPUT_TYPES,
                    shader_type='PIXEL_SHADER',
                )
            ]
        )
        screen.setup_reflection(self, "void SCREEN_SHADER(vec2 uv){ }")

        def texture_type_to_parameter(texture_type):
            sampler_type = internal_format_to_sampler_type(texture_type)
            if sampler_type == 'sampler2D':
                return Parameter('', Type.TEXTURE)
            else:
                return Parameter(sampler_type, Type.OTHER)
        
        MainPass.NODE.get_custom_outputs = self.get_mesh_shader_custom_outputs

        render_layer = PythonPipelineGraph(
            name='Render Layer',
            nodes = [ScreenPass.NODE, PrePass.NODE, MainPass.NODE, Unpack8bitTextures.NODE],
            graph_io = [
                PipelineGraphIO(
                    name = 'Render Layer',
                    function = PipelineNode.static_reflect(
                        name = 'Render Layer',
                        inputs = {
                            'Scene' : Parameter('Scene', Type.OTHER),
                        },
                        outputs = {
                            'Color' : Parameter('', Type.TEXTURE),
                        } | {k : texture_type_to_parameter(t) for k,t in self.get_render_layer_custom_outputs().items()},
                    )
                )
            ]
        )
        
        self.graphs |= {e.name : e for e in [mesh, screen, render_layer]}

        self.npr_light_shaders.setup_graphs(self, self.graphs)

    def setup_render_targets(self, resolution):
        self.t_opaque_color = Texture(resolution, GL_RGBA16F)
        self.fbo_opaque = RenderTarget([self.t_opaque_color])

        self.t_transparent_color = Texture(resolution, GL_RGBA16F)
        self.fbo_transparent = RenderTarget([self.t_transparent_color])

        self.t_color = Texture(resolution, GL_RGBA16F)
        self.fbo_color = RenderTarget([self.t_color])

        self.t_color_accumulate = Texture(resolution, GL_RGBA32F)
        self.fbo_accumulate = RenderTarget([self.t_color_accumulate])

        self.render_layer_custom_output_accumulate_textures = {}
        self.render_layer_custom_output_accumulate_fbos = {}
        
        if self.is_final_render:
            for key, texture_format in self.get_render_layer_custom_outputs().items():
                texture = Texture(resolution, texture_format)
                self.render_layer_custom_output_accumulate_textures[key] = texture
                self.render_layer_custom_output_accumulate_fbos[key] = RenderTarget([texture])
    
    def get_scene_batches(self, scene):
        opaque_batches = {}
        transparent_batches = {}
        for material, meshes in scene.batches.items():
            if material and material.shader:
                pre_pass = material.shader['MAIN_PASS']
                if 'Settings.Transparency' in pre_pass.uniforms and pre_pass.uniforms['Settings.Transparency'].value[0] == True:
                    transparent_batches[material] = meshes
                    continue
            opaque_batches[material] = meshes
        return opaque_batches, transparent_batches

    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        #SETUP SAMPLING
        if self.sampling_grid_size != scene.world_parameters['Samples.Grid Size']:
            self.sampling_grid_size = scene.world_parameters['Samples.Grid Size']
            self.samples = None

        if is_new_frame:
            self.fbo_accumulate.clear([(0,0,0,0)])
            for fbo in self.render_layer_custom_output_accumulate_fbos.values():
                fbo.clear([(0,0,0,0)])
        
        
        sample_offset = self.get_samples(scene.world_parameters['Samples.Width'])[self.sample_count]

        opaque_batches, transparent_batches = self.get_scene_batches(scene)
        
        self.npr_lighting.load(self, scene, opaque_batches, transparent_batches, sample_offset, self.sample_count)

        self.common_buffer.load(scene, resolution, sample_offset, self.sample_count)

        self.draw_layer_count = 0
        
        result = self.draw_layer(opaque_batches, scene, scene.world_parameters['Background.Color'])
        self.draw_layer_count += 1

        self.copy_textures(self.fbo_opaque, [result])
        
        self.fbo_color.clear([(0,0,0,0)])
        self.fbo_transparent.clear([(0,0,0,0)], -1)

        for i in range(scene.world_parameters['Transparency.Layers']):
            if i > 0:
                self.layer_query.begin_conditional_draw()

            self.layer_query.begin_query()
            result = self.draw_layer(transparent_batches, scene)
            self.layer_query.end_query()
            self.draw_layer_count += 1
            
            self.blend_transparency_shader.textures['IN_BACK'] = result
            self.blend_transparency_shader.textures['IN_FRONT'] = self.t_transparent_color
            self.draw_screen_pass(self.blend_transparency_shader, self.fbo_color)
            
            self.copy_textures(self.fbo_transparent, [self.t_color])
            
            if i > 0:
                self.layer_query.end_conditional_draw()

        self.blend_transparency_shader.textures['IN_BACK'] = self.t_opaque_color
        self.blend_transparency_shader.textures['IN_FRONT'] = self.t_transparent_color
        self.draw_screen_pass(self.blend_transparency_shader, self.fbo_color)

        '''
        self.fbo_opaque.clear([(1,0,0,1)])
        self.fbo_transparent.clear([(1,1,0,0.5)])
        self.fbo_color.clear([(0,0,0,1)])
        self.blend_transparency_shader.textures['IN_BACK'] = self.t_opaque_color
        self.blend_transparency_shader.textures['IN_FRONT'] = self.t_transparent_color
        self.draw_screen_pass(self.blend_transparency_shader, self.fbo_color)
        #self.blend_texture(self.t_transparent_color, self.fbo_color, 1)
        '''

        # TEMPORAL SUPER-SAMPLING ACCUMULATION
        self.blend_texture(self.t_color, self.fbo_accumulate, 1.0 / (self.sample_count + 1))

        #return {'COLOR' : self.t_color}
        
        print(self.sample_count,  1.0 / (self.sample_count + 1))
        #return {'COLOR' : self.t_color}
        
        #COMPOSITE DEPTH
        composite_depth = None
        if is_final_render:
            composite_depth = self.composite_depth.render(self, self.common_buffer, self.t_opaque_depth)
        
        return {
            'COLOR' : self.t_color_accumulate,
            'DEPTH' : composite_depth,
        } | self.render_layer_custom_output_accumulate_textures
    
    def draw_layer(self, batches, scene, background_color=(0,0,0,0)):
        graph = scene.world_parameters['Render Layer']
        if graph:
            IN = {'Scene' : scene}
            OUT = {'Color' : None}
            
            self.graphs['Render Layer'].run_source(self, graph['source'], graph['parameters'], IN, OUT)
            
            #TODO: AOV transparency ???
            if self.draw_layer_count == 0:
                for key, fbo in self.render_layer_custom_output_accumulate_fbos.items():
                    if key in OUT and OUT[key]:
                        if internal_format_to_data_format(OUT[key].internal_format) == GL_FLOAT:
                            # TEMPORAL SUPER-SAMPLING ACCUMULATION
                            self.blend_texture(OUT[key], fbo, 1.0 / (self.sample_count + 1))
            return OUT['Color']


PIPELINE = NPR_Pipeline
