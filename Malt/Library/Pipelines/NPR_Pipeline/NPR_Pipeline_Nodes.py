# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

from Malt.Library.Pipelines.NPR_Pipeline.NPR_Pipeline import *

from Malt.PipelineGraph import *

from Malt import PipelineNode

from Malt.PipelineNode import *

from Malt.Library.Nodes import Unpack8bitTextures
from Malt.Library.Pipelines.NPR_Pipeline.Nodes import ScreenPass

_COMMON_HEADER = '''
#include "NPR_Pipeline.glsl"
#include "Node Utils/node_utils.glsl"
'''

_MESH_SHADER_HEADER = _COMMON_HEADER
_MESH_SHADER_REFLECTION_SRC = _MESH_SHADER_HEADER + '''
void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO) { }
'''

_LIGHT_SHADER_HEADER = _COMMON_HEADER
_LIGHT_SHADER_REFLECTION_SRC=_LIGHT_SHADER_HEADER + '''
void LIGHT_SHADER(LightShaderInput I, inout LightShaderOutput O) { }
'''

_SCREEN_SHADER_HEADER= _COMMON_HEADER + '''
#ifdef PIXEL_SHADER
void SCREEN_SHADER(vec2 uv);
void main(){ SCREEN_SHADER(UV[0]); }
#endif //PIXEL_SHADER
'''
_SCREEN_SHADER_REFLECTION_SRC= _SCREEN_SHADER_HEADER + '''
void SCREEN_SHADER(vec2 uv){ }
'''

class NPR_Pipeline_Nodes(NPR_Pipeline):

    def __init__(self):
        super().__init__()
        self.parameters.world['Render Layer'] = Parameter('Render Layer', Type.GRAPH)
        self.render_layer_nodes = {}
        self.mesh_shader_custom_output_textures = {}
        self.render_layer_custom_output_accumulate_textures = {}
        self.render_layer_custom_output_accumulate_fbos = {}
        self.draw_layer_counter = 0
        self.setup_graphs()

    def setup_graphs(self):
        source = self.preprocess_shader_from_source(_MESH_SHADER_REFLECTION_SRC, [], ['IS_MESH_SHADER','VERTEX_SHADER','PIXEL_SHADER','REFLECTION'])
        self.graphs['Mesh Shader'] = GLSLPipelineGraph(
            pass_type=GLSLPipelineGraph.SCENE_PASS,
            file_extension='.mesh.glsl',
            root_path=SHADER_DIR,
            source=source,
            default_global_scope=_MESH_SHADER_HEADER,
            graph_io=[
                GLSLGraphIO(
                    name='COMMON_PIXEL_SHADER',
                    dynamic_input_types= GLSLGraphIO.COMMON_INPUT_TYPES,
                    dynamic_output_types= GLSLGraphIO.COMMON_OUTPUT_TYPES,
                    shader_type='PIXEL_SHADER',
                    custom_output_start_index=1,
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

        source = self.preprocess_shader_from_source(_LIGHT_SHADER_REFLECTION_SRC, [], ['IS_LIGHT_SHADER','PIXEL_SHADER','REFLECTION'])
        self.graphs['Light Shader'] = GLSLPipelineGraph(
            pass_type=GLSLPipelineGraph.INTERNAL_PASS,
            file_extension='.light.glsl',
            root_path=SHADER_DIR,
            source=source,
            default_global_scope=_LIGHT_SHADER_HEADER,
            graph_io=[ GLSLGraphIO(name='LIGHT_SHADER') ]
        )

        source = self.preprocess_shader_from_source(_SCREEN_SHADER_REFLECTION_SRC, [], ['IS_SCREEN_SHADER','PIXEL_SHADER','REFLECTION'])
        self.graphs['Screen Shader'] = GLSLPipelineGraph(
            pass_type=GLSLPipelineGraph.GLOBAL_PASS,
            file_extension='.screen.glsl',
            root_path=SHADER_DIR,
            source=source,
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

        inputs = {'Scene' : Parameter('Scene', Type.OTHER)}
        outputs = {'Color' : Parameter('Texture', Type.OTHER)}
        self.graphs['Render Layer'] = PythonPipelineGraph(self,
            [ScreenPass.NODE, Unpack8bitTextures.NODE],
            [PipelineNode.static_reflect('Render Layer', inputs, outputs)])

    def get_render_outputs(self):
        return super().get_render_outputs()

    def setup_render_targets(self, resolution):
        super().setup_render_targets(resolution)
        '''
        fbo_main_targets = [self.t_main_color, self.t_line_color, self.t_line_data]

        for key, texture_format in self.get_mesh_shader_custom_outputs().items():
            texture = Texture(resolution, texture_format)
            self.mesh_shader_custom_output_textures[key] = texture
            fbo_main_targets.append(texture)

        self.fbo_main = RenderTarget(fbo_main_targets, self.t_depth)

        if self.is_final_render:
            for key, texture_format in self.get_render_layer_custom_outputs().items():
                texture = Texture(resolution, texture_format)
                self.render_layer_custom_output_accumulate_textures[key] = texture
                self.render_layer_custom_output_accumulate_fbos[key] = RenderTarget([texture])
        '''

    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        if is_new_frame:
            for fbo in self.render_layer_custom_output_accumulate_fbos.values():
                fbo.clear([(0,0,0,0)])
        self.draw_layer_counter = 0
        result = super().do_render(resolution, scene, is_final_render, is_new_frame)
        #result.update(self.render_layer_custom_output_accumulate_textures)
        return result
    
    def draw_layer(self, batches, scene, background_color=(0,0,0,0)):
        clear_colors = [background_color, (0,0,0,1), (-1,-1,-1,-1)]
        clear_colors.extend([(0)*4] * len(self.mesh_shader_custom_output_textures))
        self.fbo_main.clear(clear_colors)
        
        IN = {'Scene' : scene}
        OUT = {'Color' : None}
        graph = scene.world_parameters['Render Layer']
        if graph:
            self.graphs['Render Layer'].run_source(graph['source'], graph['parameters'], IN, OUT)
        else:
            OUT['Color'] = super().draw_layer(batches, scene, background_color)

        '''
        #TODO: AOV transparency ???
        if self.draw_layer_counter == 0:
            for key, fbo in self.render_layer_custom_output_accumulate_fbos.items():
                if key in OUT and OUT[key]:
                    if internal_format_to_data_format(OUT[key].internal_format) == GL_FLOAT:
                        # TEMPORAL SUPER-SAMPLING ACCUMULATION
                        self.blend_texture(OUT[key], fbo, 1.0 / (self.sample_count + 1))
        '''
        #TODO: Pass as parameter
        self.draw_layer_counter += 1
        
        return OUT['Color']

        
PIPELINE = NPR_Pipeline_Nodes
