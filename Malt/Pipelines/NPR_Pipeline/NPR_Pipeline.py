# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

from os import path

from Malt.Pipeline import *
from Malt.PipelineGraph import *
from Malt.PipelineNode import PipelineNode

from Malt.GL.GL import *

from Malt.Render import Common
from Malt.Render import DepthToCompositeDepth
from Malt.Render import Sampling

from Malt.Pipelines.NPR_Pipeline.NPR_Lighting import NPR_Lighting
from Malt.Pipelines.NPR_Pipeline.NPR_LightShaders import NPR_LightShaders

from Malt.Nodes import Unpack8bitTextures

from Malt.Pipelines.NPR_Pipeline.Nodes import ScreenPass, PrePass, MainPass, SSAA, LineRender, RenderLayers

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
        default_material_path = os.path.join(os.path.dirname(__file__), 'default.mesh.glsl')
        self.parameters.world['Material.Default'] = MaterialParameter(default_material_path, '.mesh.glsl')
        self.parameters.world['Render'] = Parameter('Render', Type.GRAPH)
    
    def setup_graphs(self):
        super().setup_graphs()

        mesh = GLSLPipelineGraph(
            name='Mesh',
            graph_type=GLSLPipelineGraph.SCENE_GRAPH,
            default_global_scope=_COMMON_HEADER,
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
                    name='MAIN_PASS_PIXEL_SHADER',
                    io_wrap='MAIN_PASS',
                    shader_type='PIXEL_SHADER',
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
        
        render_layer = PythonPipelineGraph(
            name='Render Layer',
            nodes = [ScreenPass.NODE, PrePass.NODE, MainPass.NODE, Unpack8bitTextures.NODE, LineRender.NODE],
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

        render = PythonPipelineGraph(
            name='Render',
            nodes = [ScreenPass.NODE, RenderLayers.NODE, Unpack8bitTextures.NODE, SSAA.NODE, LineRender.NODE],
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
                        },
                    )
                )
            ]
        )
        
        self.graphs.update({e.name : e for e in [mesh, screen, render_layer, render]})
        NPR_LightShaders.setup_graphs(self, self.graphs)
    
    def setup_resources(self):
        super().setup_resources()
        self.common_buffer = Common.CommonBuffer()
        self.npr_lighting = NPR_Lighting(self.parameters)
        self.npr_light_shaders = NPR_LightShaders(self.parameters)
        self.composite_depth = DepthToCompositeDepth.CompositeDepth()
        global _DEFAULT_SHADER
        if _DEFAULT_SHADER is None: _DEFAULT_SHADER = self.compile_material_from_source('Mesh', _DEFAULT_SHADER_SRC)
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
        
        self.npr_lighting.load(self, scene, opaque_batches, transparent_batches, sample_offset, self.sample_count)
        self.common_buffer.load(scene, resolution, sample_offset, self.sample_count)
        
        result = None
        graph = scene.world_parameters['Render']
        if graph:
            IN = {'Scene' : scene}
            OUT = {'Color' : None}
            self.graphs['Render'].run_source(self, graph['source'], graph['parameters'], IN, OUT)
            result = OUT['Color']

        '''
        #COMPOSITE DEPTH
        composite_depth = None
        if is_final_render:
            composite_depth = self.composite_depth.render(self, self.common_buffer, self.t_opaque_depth)
        '''
        
        return {
            'COLOR' : result,
        }


PIPELINE = NPR_Pipeline
