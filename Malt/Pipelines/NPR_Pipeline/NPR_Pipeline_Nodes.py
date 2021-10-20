# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

from Malt.GL.Texture import internal_format_to_data_format
from Malt.Pipelines.NPR_Pipeline.NPR_Pipeline import *

from Malt.Parameter import GLSLPipelineGraph, PythonPipelineGraph

from Malt import PipelineNode

from Malt.PipelineNode import *

from Malt.GL.Texture import internal_format_to_vector_type, internal_format_to_sampler_type

_COMMON_HEADER = '''
#include "Pipelines/NPR_Pipeline.glsl"
#include "Node Utils/node_utils.glsl"
'''

_MESH_SHADER_HEADER = _COMMON_HEADER + '''
#ifdef PIXEL_SHADER
#ifdef MAIN_PASS
{CUSTOM_OUTPUT_LAYOUT}
#endif
#endif

void NODES_COMMON_PIXEL_SHADER(Surface S, 
    inout vec4 color,
    inout vec3 normal,
    inout uvec4 id,
    inout vec4 line_color,
    inout float line_width,
    inout vec4 transparency_shadow_color
    {CUSTOM_OUTPUT_SIGNATURE});

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{{
    {CUSTOM_OUTPUT_DECLARATION}

    NODES_COMMON_PIXEL_SHADER(S,
        PO.color,
        PO.normal,
        PO.id,
        PO.line_color,
        PO.line_width,
        PO.transparency_shadow_color
        {CUSTOM_OUTPUT_CALL});

    #ifdef PIXEL_SHADER
    #ifdef MAIN_PASS
    {{
        {CUSTOM_OUTPUT_ASIGNMENT}
    }}
    #endif
    #endif
}}

'''

_LIGHT_SHADER_HEADER = _COMMON_HEADER

_LIGHT_SHADER_REFLECTION_SRC=_LIGHT_SHADER_HEADER + '''
void LIGHT_SHADER(LightShaderInput I, inout LightShaderOutput O) { }
'''

_SCREEN_SHADER_HEADER= _COMMON_HEADER + '''
#ifdef PIXEL_SHADER

uniform sampler2D INPUT_0; uniform sampler2D INPUT_1; uniform sampler2D INPUT_2; uniform sampler2D INPUT_3;

layout (location = 0) out vec4 OUTPUT_0; layout (location = 1) out vec4 OUTPUT_1;
layout (location = 2) out vec4 OUTPUT_2; layout (location = 3) out vec4 OUTPUT_3;

void SCREEN_SHADER(vec2 uv, 
    sampler2D Input_0, sampler2D Input_1, sampler2D Input_2, sampler2D Input_3,
    out vec4 Output_0, out vec4 Output_1, out vec4 Output_2, out vec4 Output_3);

void main()
{
    SCREEN_SHADER(UV[0], 
        INPUT_0, INPUT_1, INPUT_2, INPUT_3, 
        OUTPUT_0, OUTPUT_1, OUTPUT_2, OUTPUT_3
    );
}

#endif //PIXEL_SHADER
'''

_SCREEN_SHADER_REFLECTION_SRC= _SCREEN_SHADER_HEADER + '''
void SCREEN_SHADER(vec2 uv, 
    sampler2D Input_0, sampler2D Input_1, sampler2D Input_2, sampler2D Input_3,
    out vec4 Output_0, out vec4 Output_1, out vec4 Output_2, out vec4 Output_3)
{ }
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
    
    def get_mesh_shader_custom_outputs(self):
        return {
            'Custom A' : GL_RGBA16F,
            'Custom B' : GL_RGBA16F,
            'Custom C' : GL_RGBA16F,
            'Custom D' : GL_RGBA16F,
        }
    
    def get_render_layer_custom_outputs(self):
        return {
            'Custom A' : GL_RGBA16F,
            'Custom B' : GL_RGBA16F,
            'Custom C' : GL_RGBA16F,
            'Custom D' : GL_RGBA16F,
        }
    
    def get_mesh_shader_generated_source(self):
        custom_outputs = self.get_mesh_shader_custom_outputs()
        layout = ""
        signature = ""
        declaration = ""
        call = ""
        asignment = ""
        for i, (key, texture_format) in enumerate(custom_outputs.items()):
            key = ''.join(c for c in key if c.isalnum())
            type = internal_format_to_vector_type(texture_format)
            layout += f"layout (location = {i+3}) out {type} OUT_{key};\n"
            signature += f", out {type} {key}"
            declaration += f"{type} {key} = {type}(0);\n"
            call += f", {key}"
            asignment += f"OUT_{key} = {key};\n"

        header = _MESH_SHADER_HEADER.format(
            CUSTOM_OUTPUT_LAYOUT = layout,
            CUSTOM_OUTPUT_SIGNATURE = signature,
            CUSTOM_OUTPUT_DECLARATION = declaration,
            CUSTOM_OUTPUT_CALL = call,
            CUSTOM_OUTPUT_ASIGNMENT = asignment,
        )

        common_pixel_signature = f"""void NODES_COMMON_PIXEL_SHADER(Surface S,
        inout vec4 color,
        inout vec3 normal,
        inout uvec4 id,
        inout vec4 line_color,
        inout float line_width,
        inout vec4 transparency_shadow_color
        {signature})"""
        return header, common_pixel_signature

    def setup_graphs(self):
        mesh_header, mesh_pixel_signature = self.get_mesh_shader_generated_source()
        mesh_reflection_src = mesh_header + mesh_pixel_signature + "{}\n"
        source = self.preprocess_shader_from_source(mesh_reflection_src, [], ['IS_MESH_SHADER','VERTEX_SHADER','PIXEL_SHADER','REFLECTION'])
        self.graphs['Mesh Shader'] = GLSLPipelineGraph('.mesh.glsl', source, SHADER_DIR, {
            'NODES_COMMON_PIXEL_SHADER': (None, mesh_pixel_signature),
            'VERTEX_DISPLACEMENT_SHADER': ('CUSTOM_VERTEX_DISPLACEMENT', 'vec3 VERTEX_DISPLACEMENT_SHADER(Surface S)'),
            'COMMON_VERTEX_SHADER': ('CUSTOM_VERTEX_SHADER', 'void COMMON_VERTEX_SHADER(inout Surface S)'),
        }, 
        mesh_header)
        #Remap NODES_COMMON_PIXEL_SHADER to COMMON_PIXEL_SHADER
        self.graphs['Mesh Shader'].graph_IO['COMMON_PIXEL_SHADER'] = self.graphs['Mesh Shader'].graph_IO['NODES_COMMON_PIXEL_SHADER']
        self.graphs['Mesh Shader'].graph_IO.pop('NODES_COMMON_PIXEL_SHADER')
        self.graphs['Mesh Shader'].graph_io_map['COMMON_PIXEL_SHADER'] = self.graphs['Mesh Shader'].graph_io_map['NODES_COMMON_PIXEL_SHADER']
        self.graphs['Mesh Shader'].graph_io_map.pop('NODES_COMMON_PIXEL_SHADER')

        source = self.preprocess_shader_from_source(_LIGHT_SHADER_REFLECTION_SRC, [], ['IS_LIGHT_SHADER','PIXEL_SHADER','REFLECTION'])
        self.graphs['Light Shader'] = GLSLPipelineGraph('.light.glsl', source, SHADER_DIR, {
            'LIGHT_SHADER': (None, 'void LIGHT_SHADER(LightShaderInput I, inout LightShaderOutput O)')
        },
        _LIGHT_SHADER_HEADER)

        source = self.preprocess_shader_from_source(_SCREEN_SHADER_REFLECTION_SRC, [], ['IS_SCREEN_SHADER','PIXEL_SHADER','REFLECTION'])
        self.graphs['Screen Shader'] = GLSLPipelineGraph('.screen.glsl', source, SHADER_DIR, {
            'SCREEN_SHADER': (None, '''void SCREEN_SHADER(vec2 uv, 
            sampler2D Input_0, sampler2D Input_1, sampler2D Input_2, sampler2D Input_3,
            out vec4 Output_0, out vec4 Output_1, out vec4 Output_2, out vec4 Output_3)''')
        },
        _SCREEN_SHADER_HEADER)

        def texture_type_to_parameter(texture_type):
            sampler_type = internal_format_to_sampler_type(texture_type)
            if sampler_type == 'sampler2D':
                return Parameter('', Type.TEXTURE)
            else:
                return Parameter(sampler_type, Type.OTHER) 

        inputs = {
            'Color' : Parameter('', Type.TEXTURE),
            'Normal_Depth' : Parameter('', Type.TEXTURE),
            'ID' : Parameter('', Type.TEXTURE),
            'Color (No Line)' : Parameter('', Type.TEXTURE),
            'Line Color' : Parameter('', Type.TEXTURE),
            'Line Data' : Parameter('', Type.TEXTURE),
        }
        for key, texture_type in self.get_mesh_shader_custom_outputs().items():
            inputs[key] = texture_type_to_parameter(texture_type)
        outputs = {
            'Color' : Parameter('', Type.TEXTURE),
        }
        for key, texture_type in self.get_render_layer_custom_outputs().items():
            outputs[key] = texture_type_to_parameter(texture_type)
        self.graphs['Render Layer'] = PythonPipelineGraph(self,
            [RenderScreen, Unpack8bitTextures],
            [PipelineNode.static_reflect('Render Layer', inputs, outputs)])

    def get_render_outputs(self):
        outputs = super().get_render_outputs()
        outputs.update(self.get_render_layer_custom_outputs())
        return outputs

    def setup_render_targets(self, resolution):
        super().setup_render_targets(resolution)

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

    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        if is_new_frame:
            for fbo in self.render_layer_custom_output_accumulate_fbos.values():
                fbo.clear([(0,0,0,0)])
        self.draw_layer_counter = 0
        result = super().do_render(resolution, scene, is_final_render, is_new_frame)
        result.update(self.render_layer_custom_output_accumulate_textures)
        return result
    
    def draw_layer(self, batches, scene, background_color=(0,0,0,0)):
        clear_colors = [background_color, (0,0,0,1), (-1,-1,-1,-1)]
        clear_colors.extend([(0)*4] * len(self.mesh_shader_custom_output_textures))
        self.fbo_main.clear(clear_colors)
        
        result = super().draw_layer(batches, scene, background_color)
        
        IN = {
            'Color' : result,
            'Normal_Depth' : self.t_prepass_normal_depth,
            'ID' : self.t_prepass_id,
            'Color (No Line)' : self.t_main_color,
            'Line Color' : self.t_line_color,
            'Line Data' : self.t_line_data,
        }
        IN.update(self.mesh_shader_custom_output_textures)
        OUT = { 'Color' : result }
        
        graph = scene.world_parameters['Render Layer']
        if graph:
            self.graphs['Render Layer'].run_source(graph['source'], graph['parameters'], IN, OUT)

        #TODO: AOV transparency ???
        if self.draw_layer_counter == 0:
            for key, fbo in self.render_layer_custom_output_accumulate_fbos.items():
                if key in OUT and OUT[key]:
                    if internal_format_to_data_format(OUT[key].internal_format) == GL_FLOAT:
                        # TEMPORAL SUPER-SAMPLING ACCUMULATION
                        self.blend_texture(OUT[key], fbo, 1.0 / (self.sample_count + 1))
        #TODO: Pass as parameter
        self.draw_layer_counter += 1
        
        return OUT['Color']

        
PIPELINE = NPR_Pipeline_Nodes
