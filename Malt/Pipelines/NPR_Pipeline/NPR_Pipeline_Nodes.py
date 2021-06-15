# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

from Malt.Pipelines.NPR_Pipeline.NPR_Pipeline import *

from Malt.Parameter import GLSLPipelineGraph, PythonPipelineGraph

from Malt import PipelineNode

_DEFAULT_LIGHT_SHADER_SRC='''
#include "Pipelines/NPR_Pipeline.glsl"

void LIGHT_SHADER(LightShaderInput I, inout LightShaderOutput O) { }
'''

_SCREEN_SHADER_SRC='''
#include "Pipelines/NPR_Pipeline.glsl"

#ifdef PIXEL_SHADER

uniform sampler2D INPUT_0; uniform sampler2D INPUT_1; uniform sampler2D INPUT_2; uniform sampler2D INPUT_3; 
uniform sampler2D INPUT_4; uniform sampler2D INPUT_5; uniform sampler2D INPUT_6; uniform sampler2D INPUT_7;

layout (location = 0) out vec4 OUTPUT_0; layout (location = 1) out vec4 OUTPUT_1;
layout (location = 2) out vec4 OUTPUT_2; layout (location = 3) out vec4 OUTPUT_3;
layout (location = 4) out vec4 OUTPUT_4; layout (location = 5) out vec4 OUTPUT_5;
layout (location = 6) out vec4 OUTPUT_6; layout (location = 7) out vec4 OUTPUT_7;

void SCREEN_SHADER(vec2 uv, 
    sampler2D Input_0, sampler2D Input_1, sampler2D Input_2, sampler2D Input_3,
    sampler2D Input_4, sampler2D Input_5, sampler2D Input_6, sampler2D Input_7,
    out vec4 Output_0, out vec4 Output_1, out vec4 Output_2, out vec4 Output_3,
    out vec4 Output_4, out vec4 Output_5, out vec4 Output_6, out vec4 Output_7);

void main()
{
    SCREEN_SHADER(UV[0], 
        INPUT_0, INPUT_1, INPUT_2, INPUT_3, INPUT_4, INPUT_5, INPUT_6, INPUT_7, 
        OUTPUT_0, OUTPUT_1, OUTPUT_2, OUTPUT_3, OUTPUT_4, OUTPUT_5, OUTPUT_6, OUTPUT_7
    );
}

#endif //PIXEL_SHADER
'''

_DEFAULT_SCREEN_SHADER_SRC= _SCREEN_SHADER_SRC + '''
void SCREEN_SHADER(vec2 uv, 
    sampler2D Input_0, sampler2D Input_1, sampler2D Input_2, sampler2D Input_3,
    sampler2D Input_4, sampler2D Input_5, sampler2D Input_6, sampler2D Input_7,
    out vec4 Output_0, out vec4 Output_1, out vec4 Output_2, out vec4 Output_3,
    out vec4 Output_4, out vec4 Output_5, out vec4 Output_6, out vec4 Output_7)
{ }
'''

class NPR_Pipeline_Nodes(NPR_Pipeline):

    def __init__(self):
        super().__init__()
        self.parameters.world['Render Layer'] = Parameter('Render Layer', Type.GRAPH)
        self.setup_graphs()
    
    def setup_graphs(self):
        source = self.preprocess_shader_from_source(DEFAULT_SHADER_SRC, [], ['IS_MESH_SHADER','VERTEX_SHADER','PIXEL_SHADER','NODES'])
        self.graphs['Mesh Shader'] = GLSLPipelineGraph('.mesh.glsl', source, SHADER_DIR, {
            'COMMON_PIXEL_SHADER': (None, 'void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)'),
            'VERTEX_DISPLACEMENT_SHADER': ('CUSTOM_VERTEX_DISPLACEMENT', 'vec3 VERTEX_DISPLACEMENT_SHADER(Surface S)'),
            'COMMON_VERTEX_SHADER': ('CUSTOM_VERTEX_SHADER', 'void COMMON_VERTEX_SHADER(inout Surface S)'),
        }, 
        '#include "Pipelines/NPR_Pipeline.glsl"')

        source = self.preprocess_shader_from_source(_DEFAULT_LIGHT_SHADER_SRC, [], ['IS_LIGHT_SHADER','PIXEL_SHADER','NODES'])
        self.graphs['Light Shader'] = GLSLPipelineGraph('.light.glsl', source, SHADER_DIR, {
            'LIGHT_SHADER': (None, 'void LIGHT_SHADER(LightShaderInput I, inout LightShaderOutput O)')
        },
        '#include "Pipelines/NPR_Pipeline.glsl"')

        source = self.preprocess_shader_from_source(_DEFAULT_SCREEN_SHADER_SRC, [], ['IS_SCREEN_SHADER','PIXEL_SHADER','NODES'])
        self.graphs['Screen Shader'] = GLSLPipelineGraph('.screen.glsl', source, SHADER_DIR, {
            'SCREEN_SHADER': (None, '''void SCREEN_SHADER(vec2 uv, 
            sampler2D Input_0, sampler2D Input_1, sampler2D Input_2, sampler2D Input_3,
            sampler2D Input_4, sampler2D Input_5, sampler2D Input_6, sampler2D Input_7,
            out vec4 Output_0, out vec4 Output_1, out vec4 Output_2, out vec4 Output_3,
            out vec4 Output_4, out vec4 Output_5, out vec4 Output_6, out vec4 Output_7);''')
        },
        _SCREEN_SHADER_SRC)

        inputs = {
            'Color' : Parameter('', Type.TEXTURE),
            'Normal_Depth' : Parameter('', Type.TEXTURE),
            'ID' : Parameter('ID Texture', Type.OTHER),
        }
        outputs = {
            'Color' : Parameter('', Type.TEXTURE),
        }
        self.graphs['Render Layer'] = PythonPipelineGraph(
            [PipelineNode.RenderScreen.reflect()],
            [PipelineNode.PipelineNode.static_reflect('Render Layer', inputs, outputs)])

    def setup_render_targets(self, resolution):
        super().setup_render_targets(resolution)

    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        return super().do_render(resolution, scene, is_final_render, is_new_frame)
    
    def draw_layer(self, batches, scene, background_color=(0,0,0,0)):
        print('-'*10)
        print(scene.world_parameters['Render Layer']['parameters'])
        return super().draw_layer(batches, scene, background_color)
        
PIPELINE = NPR_Pipeline_Nodes
