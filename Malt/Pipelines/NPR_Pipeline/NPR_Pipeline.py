from os import path
from Malt.GL.RenderTarget import RenderTarget
from Malt.GL.Texture import Texture

from Malt.Pipeline import *
from Malt.PipelineGraph import *
from Malt.PipelineNode import PipelineNode

from Malt.GL.GL import *

from Malt.Render import DepthToCompositeDepth
from Malt.Render import Sampling

_SCREEN_SHADER_HEADER='''
#include "NPR_ScreenShader.glsl"
#include "Node Utils/node_utils.glsl"
'''

_MESH_SHADER_HEADER='''
#include "NPR_MeshShader.glsl"
#include "Node Utils/node_utils.glsl"
'''

_LIGHT_SHADER_HEADER='''
#include "NPR_LightShader.glsl"
#include "Node Utils/node_utils.glsl"
'''

_DEFAULT_SHADER = None

_DEFAULT_SHADER_SRC='''
void PRE_PASS_PIXEL_SHADER(inout PrePassOutput PPO){ }
void DEPTH_OFFSET(inout float depth_offset, inout bool offset_position){ }

#ifdef MAIN_PASS
layout (location = 0) out vec4 OUT_0;
layout (location = 1) out vec4 OUT_1;
layout (location = 2) out vec4 OUT_2;
layout (location = 3) out vec4 OUT_3;
layout (location = 4) out vec4 OUT_4;
layout (location = 5) out vec4 OUT_5;
layout (location = 6) out vec4 OUT_6;
layout (location = 7) out vec4 OUT_7;
#endif //MAIN_PASS

void MAIN_PASS_PIXEL_SHADER()
{    
    #ifdef MAIN_PASS
    {
        OUT_0 = vec4(1,1,0,1);
        OUT_1 = vec4(1,1,0,1);
        OUT_2 = vec4(1,1,0,1);
        OUT_3 = vec4(1,1,0,1);
        OUT_4 = vec4(1,1,0,1);
        OUT_5 = vec4(1,1,0,1);
        OUT_6 = vec4(1,1,0,1);
        OUT_7 = vec4(1,1,0,1);
    }
    #endif //MAIN_PASS
}
'''

class NPR_Pipeline(Pipeline):

    def __init__(self, plugins=[]):
        shader_dir = path.join(path.dirname(__file__), 'Shaders')
        if shader_dir not in self.SHADER_INCLUDE_PATHS:
            self.SHADER_INCLUDE_PATHS.append(shader_dir)
        self.sampling_grid_size = 1
        self.samples = None
        super().__init__(plugins)
    
    def setup_parameters(self):
        super().setup_parameters()
        self.parameters.world['Samples.Grid Size'] = Parameter(8, Type.INT)
        self.parameters.world['Samples.Grid Size @ Preview'] = Parameter(4, Type.INT)
        self.parameters.world['Samples.Width'] = Parameter(1.0, Type.FLOAT)
        defaults_path = os.path.join(os.path.dirname(__file__), 'Defaults', 'defaults')
        self.parameters.world['Material.Default'] = MaterialParameter((defaults_path, 'Malt - Default Mesh Material'), '.mesh.glsl')
        self.parameters.world['Render'] = GraphParameter((defaults_path, 'Default Render'), 'Render')
        self.parameters.light['Light Group'] = Parameter(1, Type.INT)
        self.parameters.light['Shader'] = MaterialParameter('', '.light.glsl')
        self.parameters.material['Light Groups.Light'] = Parameter([1,0,0,0], Type.INT, 4, '.mesh.glsl')
        self.parameters.material['Light Groups.Shadow'] = Parameter([1,0,0,0], Type.INT, 4, '.mesh.glsl')
    
    def setup_graphs(self):
        super().setup_graphs()

        mesh = GLSLPipelineGraph(
            name='Mesh',
            graph_type=GLSLPipelineGraph.SCENE_GRAPH,
            default_global_scope=_MESH_SHADER_HEADER,
            default_shader_src=_DEFAULT_SHADER_SRC,
            shaders=['PRE_PASS', 'MAIN_PASS', 'SHADOW_PASS'],
            graph_io=[
                GLSLGraphIO(
                    name='PRE_PASS_PIXEL_SHADER',
                    define='CUSTOM_PRE_PASS',
                    io_wrap='PRE_PASS',
                    shader_type='PIXEL_SHADER',
                    dynamic_output_types=GLSLGraphIO.COMMON_OUTPUT_TYPES,
                    custom_output_start_index=2,
                ),
                GLSLGraphIO(
                    name='DEPTH_OFFSET',
                    define='CUSTOM_DEPTH_OFFSET',
                    shader_type='PIXEL_SHADER',
                ),
                GLSLGraphIO(
                    name='MAIN_PASS_PIXEL_SHADER',
                    io_wrap='MAIN_PASS',
                    shader_type='PIXEL_SHADER',
                    dynamic_input_types=GLSLGraphIO.COMMON_INPUT_TYPES,
                    dynamic_output_types=GLSLGraphIO.COMMON_OUTPUT_TYPES,
                    default_dynamic_outputs={
                        'Color': 'vec4',
                        'Line Color': 'vec4',
                        'Line Width': 'float',
                    }
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
        self.add_graph(mesh)

        screen = GLSLPipelineGraph(
            name='Screen',
            graph_type=GLSLPipelineGraph.GLOBAL_GRAPH,
            default_global_scope=_SCREEN_SHADER_HEADER,
            default_shader_src="void SCREEN_SHADER(){ }",
            graph_io=[ 
                GLSLGraphIO(
                    name='SCREEN_SHADER',
                    shader_type='PIXEL_SHADER',
                    dynamic_input_types= GLSLGraphIO.COMMON_INPUT_TYPES,
                    dynamic_output_types= GLSLGraphIO.COMMON_OUTPUT_TYPES,
                    default_dynamic_outputs={
                        'Color': 'vec4',
                    }
                )
            ]
        )
        self.add_graph(screen)

        light = GLSLPipelineGraph(
            name='Light',
            graph_type=GLSLPipelineGraph.INTERNAL_GRAPH,
            default_global_scope=_LIGHT_SHADER_HEADER,
            default_shader_src="void LIGHT_SHADER(LightShaderInput I, inout LightShaderOutput O) { }",
            graph_io=[ 
                GLSLGraphIO(
                    name='LIGHT_SHADER',
                    shader_type='PIXEL_SHADER',
                )
            ]
        )
        self.add_graph(light)
        
        render_layer = PythonPipelineGraph(
            name='Render Layer',
            graph_io = [
                PythonGraphIO(
                    name = 'Render Layer',
                    dynamic_input_types= PythonGraphIO.COMMON_IO_TYPES,
                    dynamic_output_types= PythonGraphIO.COMMON_IO_TYPES,
                    function = PipelineNode.static_reflect(
                        name = 'Render Layer',
                        inputs = {
                            'Scene' : Parameter('Scene', Type.OTHER),
                        },
                        outputs = {
                            'Color' : Parameter('', Type.TEXTURE),
                        },
                    )
                )
            ]
        )
        render_layer.add_library(os.path.join(os.path.dirname(__file__),'..','..','Nodes'))
        render_layer.add_library(os.path.join(os.path.dirname(__file__), 'Nodes', 'RenderLayer'))
        self.add_graph(render_layer)

        render = PythonPipelineGraph(
            name='Render',
            graph_io = [
                PythonGraphIO(
                    name = 'Render',
                    dynamic_output_types= PythonGraphIO.COMMON_IO_TYPES,
                    function = PipelineNode.static_reflect(
                        name = 'Render',
                        inputs = {
                            'Scene' : Parameter('Scene', Type.OTHER),
                        },
                        outputs = {
                            'Color' : Parameter('', Type.TEXTURE),
                            'Depth' : Parameter('', Type.TEXTURE),
                        },
                    )
                )
            ]
        )
        render.add_library(os.path.join(os.path.dirname(__file__),'..','..','Nodes'))
        render.add_library(os.path.join(os.path.dirname(__file__), 'Nodes', 'Render'))
        self.add_graph(render)
        
    
    def setup_resources(self):
        super().setup_resources()
        self.composite_depth = DepthToCompositeDepth.CompositeDepth()
        global _DEFAULT_SHADER
        if _DEFAULT_SHADER is None: _DEFAULT_SHADER = self.compile_material_from_source('Mesh', _MESH_SHADER_HEADER + _DEFAULT_SHADER_SRC)
        self.default_shader = _DEFAULT_SHADER
    
    def get_samples(self):
        if self.samples is None:
            self.samples = Sampling.get_RGSS_samples(self.sampling_grid_size, 1.0)
        return self.samples
    
    def get_sample(self, width):
        w, h = self.get_samples()[self.sample_count]
        w*=width
        h*=width
        return w, h
    
    def get_scene_batches(self, scene):
        opaque_batches = {}
        transparent_batches = {}
        for material, meshes in scene.batches.items():
            if material and material.shader:
                if material.shader['PRE_PASS'].uniforms['Settings.Transparency'].value[0] == True:
                    transparent_batches[material] = meshes
                    continue
            opaque_batches[material] = meshes
        return opaque_batches, transparent_batches

    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        #SETUP SAMPLING
        if self.sampling_grid_size != scene.world_parameters['Samples.Grid Size']:
            self.sampling_grid_size = scene.world_parameters['Samples.Grid Size']
            self.samples = None
        
        self.is_new_frame = is_new_frame
        
        sample_offset = self.get_sample(scene.world_parameters['Samples.Width'])

        opaque_batches, transparent_batches = self.get_scene_batches(scene)
        
        self.common_buffer.load(scene, resolution, sample_offset, self.sample_count)
        scene.shader_resources = {
            'COMMON_UNIFORMS' : self.common_buffer
        }
        
        result = {
            'COLOR': None,
            'DEPTH': None,
        }
        graph = scene.world_parameters['Render']
        if graph:
            IN = {'Scene' : scene}
            OUT = {'Color' : None}
            self.graphs['Render'].run_source(self, graph['source'], graph['parameters'], IN, OUT)
            result = OUT
            result['COLOR'] = result['Color']
            result['DEPTH'] = result['Depth']

        #COMPOSITE DEPTH
        if is_final_render and result['DEPTH'] is None:
            if self.sample_count == len(self.samples) - 1:
                normal_depth = Texture(resolution, GL_RGBA32F)
                target = RenderTarget([normal_depth], Texture(resolution, GL_DEPTH_COMPONENT32F))
                target.clear([(0,0,1,1)], 1)
                self.common_buffer.load(scene, resolution)
                self.draw_scene_pass(target, opaque_batches, 'PRE_PASS', self.default_shader, scene.shader_resources)
                result['DEPTH'] = self.composite_depth.render(self, self.common_buffer, normal_depth, depth_channel=3)
        
        return result


PIPELINE = NPR_Pipeline
