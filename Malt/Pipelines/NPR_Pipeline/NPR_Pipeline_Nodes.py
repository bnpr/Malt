# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

from Malt.Pipelines.NPR_Pipeline.NPR_Pipeline import *

from Malt.Parameter import GLSLPipelineGraph, PythonPipelineGraph

from Malt import PipelineNode

from Malt.PipelineNode import *

_COMMON_HEADER = '''
#include "Pipelines/NPR_Pipeline.glsl"
#include "Node Utils/node_utils.glsl"
'''

_MESH_SHADER_HEADER = _COMMON_HEADER + '''
#ifdef PIXEL_SHADER
#ifdef MAIN_PASS

layout (location = 4) out vec4 OUTPUT_0;
layout (location = 5) out vec4 OUTPUT_1;
layout (location = 6) out vec4 OUTPUT_2;
layout (location = 7) out vec4 OUTPUT_3;

#endif
#endif

void NODES_COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO,
    out vec4 Output_0, out vec4 Output_1, out vec4 Output_2, out vec4 Output_3);

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec4 custom_outputs[4];

    NODES_COMMON_PIXEL_SHADER(S, PO, custom_outputs[0], custom_outputs[1], custom_outputs[2], custom_outputs[3]);

    #ifdef PIXEL_SHADER
    #ifdef MAIN_PASS
    {
        OUTPUT_0 = custom_outputs[0];
        OUTPUT_1 = custom_outputs[1];
        OUTPUT_2 = custom_outputs[2];
        OUTPUT_3 = custom_outputs[3];
    }
    #endif
    #endif
}

'''

_MESH_SHADER_REFLECTION_SRC = _MESH_SHADER_HEADER + '''
void NODES_COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO,
    out vec4 Output_0, out vec4 Output_1, out vec4 Output_2, out vec4 Output_3)
{
    PO.color.rgb = vec3(1,1,0);
}
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
        self.setup_graphs()
    
    def setup_graphs(self):
        source = self.preprocess_shader_from_source(_MESH_SHADER_REFLECTION_SRC, [], ['IS_MESH_SHADER','VERTEX_SHADER','PIXEL_SHADER','NODES'])
        self.graphs['Mesh Shader'] = GLSLPipelineGraph('.mesh.glsl', source, SHADER_DIR, {
            'NODES_COMMON_PIXEL_SHADER': (None, '''void NODES_COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO,
            out vec4 Output_0, out vec4 Output_1, out vec4 Output_2, out vec4 Output_3)'''),
            'VERTEX_DISPLACEMENT_SHADER': ('CUSTOM_VERTEX_DISPLACEMENT', 'vec3 VERTEX_DISPLACEMENT_SHADER(Surface S)'),
            'COMMON_VERTEX_SHADER': ('CUSTOM_VERTEX_SHADER', 'void COMMON_VERTEX_SHADER(inout Surface S)'),
        }, 
        _MESH_SHADER_HEADER)
        #Remap NODES_COMMON_PIXEL_SHADER to COMMON_PIXEL_SHADER
        self.graphs['Mesh Shader'].graph_IO['COMMON_PIXEL_SHADER'] = self.graphs['Mesh Shader'].graph_IO['NODES_COMMON_PIXEL_SHADER']
        self.graphs['Mesh Shader'].graph_IO.pop('NODES_COMMON_PIXEL_SHADER')
        self.graphs['Mesh Shader'].graph_io_map['COMMON_PIXEL_SHADER'] = self.graphs['Mesh Shader'].graph_io_map['NODES_COMMON_PIXEL_SHADER']
        self.graphs['Mesh Shader'].graph_io_map.pop('NODES_COMMON_PIXEL_SHADER')
        

        source = self.preprocess_shader_from_source(_LIGHT_SHADER_REFLECTION_SRC, [], ['IS_LIGHT_SHADER','PIXEL_SHADER','NODES'])
        self.graphs['Light Shader'] = GLSLPipelineGraph('.light.glsl', source, SHADER_DIR, {
            'LIGHT_SHADER': (None, 'void LIGHT_SHADER(LightShaderInput I, inout LightShaderOutput O)')
        },
        _LIGHT_SHADER_HEADER)

        source = self.preprocess_shader_from_source(_SCREEN_SHADER_REFLECTION_SRC, [], ['IS_SCREEN_SHADER','PIXEL_SHADER','NODES'])
        self.graphs['Screen Shader'] = GLSLPipelineGraph('.screen.glsl', source, SHADER_DIR, {
            'SCREEN_SHADER': (None, '''void SCREEN_SHADER(vec2 uv, 
            sampler2D Input_0, sampler2D Input_1, sampler2D Input_2, sampler2D Input_3,
            out vec4 Output_0, out vec4 Output_1, out vec4 Output_2, out vec4 Output_3)''')
        },
        _SCREEN_SHADER_HEADER)

        inputs = {
            'Color' : Parameter('', Type.TEXTURE),
            'Normal_Depth' : Parameter('', Type.TEXTURE),
            'ID' : Parameter('ID Texture', Type.OTHER),
            'Input 0' : Parameter('', Type.TEXTURE),
            'Input 1' : Parameter('', Type.TEXTURE),
            'Input 2' : Parameter('', Type.TEXTURE),
            'Input 3' : Parameter('', Type.TEXTURE),
        }
        outputs = {
            'Color' : Parameter('', Type.TEXTURE),
        }
        self.graphs['Render Layer'] = PythonPipelineGraph(self,
            [RenderScreen],
            [PipelineNode.static_reflect('Render Layer', inputs, outputs)])

    def setup_render_targets(self, resolution):
        super().setup_render_targets(resolution)

        self.t_main_output_0 = Texture(resolution, GL_RGBA16F)
        self.t_main_output_1 = Texture(resolution, GL_RGBA16F)
        self.t_main_output_2 = Texture(resolution, GL_RGBA16F)
        self.t_main_output_3 = Texture(resolution, GL_RGBA16F)
        self.fbo_main = RenderTarget([self.t_main_color, self.t_line_color, self.t_line_data, None,
        self.t_main_output_0, self.t_main_output_1, self.t_main_output_2, self.t_main_output_3], self.t_depth)

    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        return super().do_render(resolution, scene, is_final_render, is_new_frame)
    
    def draw_layer(self, batches, scene, background_color=(0,0,0,0)):
        self.fbo_main.clear([background_color, (0,0,0,1), (-1,-1,-1,-1), (0)*4, (0)*4, (0)*4, (0)*4, (0)*4])
        result = super().draw_layer(batches, scene, background_color)
        IO = {
            'Color' : result,
            'Normal_Depth' : self.t_prepass_normal_depth,
            'ID' : self.t_prepass_id,
            'Input 0' : self.t_main_output_0,
            'Input 1' : self.t_main_output_1,
            'Input 2' : self.t_main_output_2,
            'Input 3' : self.t_main_output_3,
        }
        graph = scene.world_parameters['Render Layer']
        if graph:
            self.graphs['Render Layer'].run_source(graph['source'], graph['parameters'], IO)
        return IO['Color']

        
PIPELINE = NPR_Pipeline_Nodes
