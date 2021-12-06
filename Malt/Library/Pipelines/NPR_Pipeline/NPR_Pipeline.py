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
from Malt.Library.Render import Lighting as Lighting
from Malt.Library.Render import Sampling

from Malt.Library.Pipelines.NPR_Pipeline import NPR_Lighting

from Malt.Library.Nodes import Unpack8bitTextures

from Malt.Library.Pipelines.NPR_Pipeline.Nodes import ScreenPass

_COMMON_HEADER = '''
#include "NPR_Pipeline.glsl"
#include "Node Utils/node_utils.glsl"
'''

_SCREEN_SHADER_HEADER= _COMMON_HEADER + '''
#ifdef PIXEL_SHADER
void SCREEN_SHADER(vec2 uv);
void main(){ SCREEN_SHADER(UV[0]); }
#endif //PIXEL_SHADER
'''

_DEFAULT_SHADER = None

_DEFAULT_SHADER_SRC='''
#include "NPR_Pipeline.glsl"

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    PO.color.rgb = vec3(1,1,0);
}
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

        self.setup_graphs()
        
        self.sampling_grid_size = 2
        self.samples = None

        self.parameters.world['Background.Color'] = Parameter((0.5,0.5,0.5,1), Type.FLOAT, 4)
        
        self.parameters.world['Samples.Grid Size'] = Parameter(8, Type.INT)
        self.parameters.world['Samples.Grid Size @ Preview'] = Parameter(4, Type.INT)
        self.parameters.world['Samples.Width'] = Parameter(1.5, Type.FLOAT)
        
        self.parameters.world['ShadowMaps.Sun.Cascades.Distribution Scalar'] = Parameter(0.9, Type.FLOAT)
        self.parameters.world['ShadowMaps.Sun.Cascades.Count'] = Parameter(4, Type.INT)
        self.parameters.world['ShadowMaps.Sun.Cascades.Count @ Preview'] = Parameter(2, Type.INT)
        self.parameters.world['ShadowMaps.Sun.Cascades.Max Distance'] = Parameter(100, Type.FLOAT)
        self.parameters.world['ShadowMaps.Sun.Cascades.Max Distance @ Preview'] = Parameter(25, Type.FLOAT)
        self.parameters.world['ShadowMaps.Sun.Resolution'] = Parameter(2048, Type.INT)
        self.parameters.world['ShadowMaps.Spot.Resolution'] = Parameter(2048, Type.INT)
        self.parameters.world['ShadowMaps.Spot.Resolution @ Preview'] = Parameter(512, Type.INT)
        self.parameters.world['ShadowMaps.Point.Resolution'] = Parameter(2048, Type.INT)
        self.parameters.world['ShadowMaps.Point.Resolution @ Preview'] = Parameter(512, Type.INT)
        
        self.parameters.world['Transparency.Layers'] = Parameter(4, Type.INT)
        self.parameters.world['Transparency.Layers @ Preview'] = Parameter(1, Type.INT)
        
        default_material_path = os.path.join(os.path.dirname(__file__), 'default.mesh.glsl')
        self.parameters.world['Material.Default'] = MaterialParameter(default_material_path, '.mesh.glsl')
        
        self.parameters.light['Shader'] = MaterialParameter('', '.light.glsl')
        self.parameters.light['Light Group'] = Parameter(1, Type.INT)
        
        self.parameters.material['Light Groups.Light'] = Parameter([1,0,0,0], Type.INT, 4, 'mesh')
        self.parameters.material['Light Groups.Shadow'] = Parameter([1,0,0,0], Type.INT, 4, 'mesh')

        self.parameters.world['Render Layer'] = Parameter('Render Layer', Type.GRAPH)
        self.render_layer_nodes = {}

        global _DEFAULT_SHADER
        if _DEFAULT_SHADER is None: _DEFAULT_SHADER = self.compile_material_from_source('Mesh', _DEFAULT_SHADER_SRC)
        self.default_shader = _DEFAULT_SHADER

        global _BLEND_TRANSPARENCY_SHADER
        if _BLEND_TRANSPARENCY_SHADER is None: _BLEND_TRANSPARENCY_SHADER = self.compile_shader_from_source(_BLEND_TRANSPARENCY_SHADER_SRC)
        self.blend_transparency_shader = _BLEND_TRANSPARENCY_SHADER

        self.common_buffer = Common.CommonBuffer()
        self.lights_buffer = Lighting.get_lights_buffer()
        self.light_groups_buffer = NPR_Lighting.NPR_LightsGroupsBuffer()
        self.shadowmaps_opaque, self.shadowmaps_transparent = NPR_Lighting.get_shadow_maps()
        self.custom_light_shading = NPR_Lighting.NPR_LightShaders()

        self.composite_depth = DepthToCompositeDepth.CompositeDepth()

        self.layer_query = None

    def get_mesh_shader_custom_outputs(self):
        return {
            'Line Color' : GL_RGBA16F,
            'Line Width' : GL_RGBA16F,
        }
    
    def get_render_layer_custom_outputs(self):
        return {}
    
    def get_render_outputs(self):
        return super().get_render_outputs() | self.get_render_layer_custom_outputs()
    
    def get_samples(self, width=1.0):
        if self.samples is None:
            self.samples = Sampling.get_RGSS_samples(self.sampling_grid_size, width)
        return self.samples
    
    def get_mesh_shader_generated_source(self):
        from textwrap import dedent
        header = _COMMON_HEADER + dedent('''
        #ifdef PIXEL_SHADER
        #ifdef MAIN_PASS
        {CUSTOM_OUTPUT_LAYOUT}
        #endif
        #endif

        void CUSTOM_COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO {CUSTOM_OUTPUT_SIGNATURE});

        void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
        {{
            {CUSTOM_OUTPUT_DECLARATION}

            CUSTOM_COMMON_PIXEL_SHADER(S, PO {CUSTOM_OUTPUT_CALL});

            #ifdef PIXEL_SHADER
            #ifdef MAIN_PASS
            {{
                {CUSTOM_OUTPUT_ASIGNMENT}
            }}
            #endif
            #endif
        }}
        ''')
        custom_outputs = self.get_mesh_shader_custom_outputs()
        layout = ""
        signature = ""
        declaration = ""
        call = ""
        asignment = ""
        for i, (key, texture_format) in enumerate(custom_outputs.items()):
            key = ''.join(c for c in key if c.isalnum())
            type = internal_format_to_vector_type(texture_format)
            layout += f"layout (location = {i+1}) out {type} OUT_{key};\n"
            signature += f", inout {type} {key}"
            declaration += f"{type} {key} = {type}(0);\n"
            call += f", {key}"
            asignment += f"OUT_{key} = {key};\n"

        header = header.format(
            CUSTOM_OUTPUT_LAYOUT = layout,
            CUSTOM_OUTPUT_SIGNATURE = signature,
            CUSTOM_OUTPUT_DECLARATION = declaration,
            CUSTOM_OUTPUT_CALL = call,
            CUSTOM_OUTPUT_ASIGNMENT = asignment,
        )

        reflection_src = f"void CUSTOM_COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO {signature}) {{}}\n"
        return header, reflection_src
    
    def setup_graphs(self):
        mesh_header, mesh_src = self.get_mesh_shader_generated_source()
        mesh = GLSLPipelineGraph(
            name='Mesh',
            default_global_scope=mesh_header,
            shaders=['PRE_PASS', 'MAIN_PASS', 'SHADOW_PASS'],
            graph_io=[
                GLSLGraphIO(
                    name='CUSTOM_COMMON_PIXEL_SHADER',
                    shader_type='PIXEL_SHADER',
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
        mesh.setup_reflection(self, mesh_src)

        light = GLSLPipelineGraph(
            name='Light',
            default_global_scope=_COMMON_HEADER,
            graph_io=[ 
                GLSLGraphIO(
                    name='LIGHT_SHADER',
                    shader_type='PIXEL_SHADER',
                )
            ]
        )
        light.setup_reflection(self, "void LIGHT_SHADER(LightShaderInput I, inout LightShaderOutput O) { }")

        screen = GLSLPipelineGraph(
            name='Screen',
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

        render_layer = PythonPipelineGraph(
            name='Render Layer',
            nodes = [ScreenPass.NODE, Unpack8bitTextures.NODE],
            graph_io = [
                PipelineGraphIO(
                    name = 'Render Layer',
                    function = PipelineNode.static_reflect(
                        name = 'Render Layer',
                        inputs = {
                            'Color' : Parameter('', Type.TEXTURE),
                            'Normal_Depth' : Parameter('', Type.TEXTURE),
                            'ID' : Parameter('', Type.TEXTURE),
                        } | {k : texture_type_to_parameter(t) for k,t in self.get_mesh_shader_custom_outputs().items()},
                        outputs = {
                            'Color' : Parameter('', Type.TEXTURE),
                        } | {k : texture_type_to_parameter(t) for k,t in self.get_render_layer_custom_outputs().items()},
                    )
                )
            ]
        )
        
        self.graphs = {e.name : e for e in [mesh, light, screen, render_layer]}

    def setup_render_targets(self, resolution):
        self.t_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        
        self.t_prepass_normal_depth = Texture(resolution, GL_RGBA32F)
        self.t_prepass_id = Texture(resolution, GL_RGBA16UI, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        self.fbo_prepass = RenderTarget([self.t_prepass_normal_depth, self.t_prepass_id], self.t_depth)
        
        self.t_last_layer_id = Texture(resolution, GL_R16UI, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        self.fbo_last_layer_id = RenderTarget([self.t_last_layer_id])

        self.mesh_shader_custom_output_textures = {}
        self.render_layer_custom_output_accumulate_textures = {}
        self.render_layer_custom_output_accumulate_fbos = {}
        
        self.t_main_color = Texture(resolution, GL_RGBA16F)
        fbo_main_targets = [self.t_main_color]
        for key, texture_format in self.get_mesh_shader_custom_outputs().items():
            texture = Texture(resolution, texture_format)
            self.mesh_shader_custom_output_textures[key] = texture
            fbo_main_targets.append(texture)
        self.fbo_main = RenderTarget(fbo_main_targets, self.t_depth)

        self.t_opaque_color = Texture(resolution, GL_RGBA16F)
        self.t_opaque_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        self.fbo_opaque = RenderTarget([self.t_opaque_color], self.t_opaque_depth)

        self.t_transparent_color = Texture(resolution, GL_RGBA16F)
        self.t_transparent_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        self.fbo_transparent = RenderTarget([self.t_transparent_color], self.t_transparent_depth)

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

    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        #SETUP SAMPLING
        if self.sampling_grid_size != scene.world_parameters['Samples.Grid Size']:
            self.sampling_grid_size = scene.world_parameters['Samples.Grid Size']
            self.samples = None

        if is_new_frame:
            self.fbo_accumulate.clear([(0,0,0,0)])
            for fbo in self.render_layer_custom_output_accumulate_fbos.values():
                fbo.clear([(0,0,0,0)])

        self.fbo_opaque.clear([(0,0,0,0)])
        self.fbo_color.clear([(0,0,0,0)])
        
        sample_offset = self.get_samples(scene.world_parameters['Samples.Width'])[self.sample_count]

        self.draw_layer_counter = 0

        #SETUP SCENE BATCHES
        opaque_batches = {}
        transparent_batches = {}
        for material, meshes in scene.batches.items():
            if material and material.shader:
                if material.shader['MAIN_PASS'].uniforms['Settings.Transparency'].value[0] == True:
                    transparent_batches[material] = meshes
                    continue
            opaque_batches[material] = meshes

        #SETUP UNIFORM BLOCKS
        self.common_buffer.load(scene, resolution, sample_offset, self.sample_count)
        self.lights_buffer.load(scene, 
            scene.world_parameters['ShadowMaps.Sun.Cascades.Count'], 
            scene.world_parameters['ShadowMaps.Sun.Cascades.Distribution Scalar'],
            scene.world_parameters['ShadowMaps.Sun.Cascades.Max Distance'], sample_offset)
        self.light_groups_buffer.load(scene)
        self.shadowmaps_opaque.load(scene,
            scene.world_parameters['ShadowMaps.Spot.Resolution'],
            scene.world_parameters['ShadowMaps.Sun.Resolution'],
            scene.world_parameters['ShadowMaps.Point.Resolution'],
            scene.world_parameters['ShadowMaps.Sun.Cascades.Count'])
        self.shadowmaps_transparent.load(scene,
            scene.world_parameters['ShadowMaps.Spot.Resolution'],
            scene.world_parameters['ShadowMaps.Sun.Resolution'],
            scene.world_parameters['ShadowMaps.Point.Resolution'],
            scene.world_parameters['ShadowMaps.Sun.Cascades.Count'])
        
        UBOS = {
            'COMMON_UNIFORMS' : self.common_buffer,
            'SCENE_LIGHTS' : self.lights_buffer
        }

        #RENDER SHADOWMAPS
        def render_shadow_passes(lights, fbos_opaque, fbos_transparent, sample_offset = sample_offset):
            for light_index, light_matrices_pair in enumerate(lights.items()):
                light, matrices = light_matrices_pair
                for matrix_index, camera_projection_pair in enumerate(matrices): 
                    camera, projection = camera_projection_pair
                    i = light_index * len(matrices) + matrix_index
                    self.common_buffer.load(scene, fbos_opaque[i].resolution, sample_offset, self.sample_count, camera, projection)
                    def get_light_group_batches(batches):
                        result = {}
                        for material, meshes in batches.items():
                            if material and light.parameters['Light Group'] in material.parameters['Light Groups.Shadow']:
                                result[material] = meshes
                        return result
                    self.draw_scene_pass(fbos_opaque[i], get_light_group_batches(opaque_batches), 
                        'SHADOW_PASS', self.default_shader['SHADOW_PASS'], UBOS)
                    self.draw_scene_pass(fbos_transparent[i], get_light_group_batches(transparent_batches), 
                        'SHADOW_PASS', self.default_shader['SHADOW_PASS'], UBOS)
        
        render_shadow_passes(self.lights_buffer.spots,
            self.shadowmaps_opaque.spot_fbos, self.shadowmaps_transparent.spot_fbos)
        
        glEnable(GL_DEPTH_CLAMP)
        render_shadow_passes(self.lights_buffer.suns,
            self.shadowmaps_opaque.sun_fbos, self.shadowmaps_transparent.sun_fbos)
        glDisable(GL_DEPTH_CLAMP)

        render_shadow_passes(self.lights_buffer.points,
            self.shadowmaps_opaque.point_fbos, self.shadowmaps_transparent.point_fbos, (0,0))

        #SCENE RENDER
        #Load scene camera settings
        self.common_buffer.load(scene, resolution, sample_offset, self.sample_count)

        result = self.draw_layer(opaque_batches, scene, scene.world_parameters['Background.Color'])

        self.copy_textures(self.fbo_opaque, [result], self.t_depth)
        
        self.fbo_transparent.clear([(0,0,0,0)], -1)
        self.fbo_last_layer_id.clear([(0,0,0,0)])

        for i in range(scene.world_parameters['Transparency.Layers']):
            if i > 0:
                glBeginConditionalRender(self.layer_query[0], GL_QUERY_WAIT)
            result = self.draw_layer(transparent_batches, scene)
            self.draw_layer_counter += 1
            self.copy_textures(self.fbo_last_layer_id, [self.t_prepass_id])

            self.blend_transparency_shader.textures['IN_BACK'] = result
            self.blend_transparency_shader.textures['IN_FRONT'] = self.t_transparent_color
            self.draw_screen_pass(self.blend_transparency_shader, self.fbo_color)
            
            self.copy_textures(self.fbo_transparent, [self.t_color], self.t_depth)
            if i > 0:
                glEndConditionalRender()

        self.blend_transparency_shader.textures['IN_BACK'] = self.t_opaque_color
        self.blend_transparency_shader.textures['IN_FRONT'] = self.t_transparent_color
        self.draw_screen_pass(self.blend_transparency_shader, self.fbo_color)

        # TEMPORAL SUPER-SAMPLING ACCUMULATION
        self.blend_texture(self.t_color, self.fbo_accumulate, 1.0 / (self.sample_count + 1))

        #COMPOSITE DEPTH
        composite_depth = None
        if is_final_render:
            composite_depth = self.composite_depth.render(self, self.common_buffer, self.t_opaque_depth)
        
        return {
            'COLOR' : self.t_color_accumulate,
            'DEPTH' : composite_depth,
        } | self.render_layer_custom_output_accumulate_textures
    
    def draw_layer(self, batches, scene, background_color=(0,0,0,0)):
        UBOS = {
            'COMMON_UNIFORMS' : self.common_buffer,
            'SCENE_LIGHTS' : self.lights_buffer
        }
        
        callbacks = [
            lambda shader : self.light_groups_buffer.shader_callback(shader),
            lambda shader : self.shadowmaps_opaque.shader_callback(shader),
            lambda shader : self.shadowmaps_transparent.shader_callback(shader),
        ]

        #PRE-PASS
        textures = {
            'IN_OPAQUE_COLOR': self.t_opaque_color,
            'IN_OPAQUE_DEPTH': self.t_opaque_depth,
            'IN_TRANSPARENT_DEPTH': self.t_transparent_depth,
            'IN_LAST_ID': self.t_last_layer_id,
        }
        self.fbo_prepass.clear([(0,0,1,1), (0,0,0,0)], 1, 0)

        if self.layer_query:
            glDeleteQueries(1, self.layer_query)
        self.layer_query = gl_buffer(GL_UNSIGNED_INT, 1)
        glGenQueries(1, self.layer_query)
        glBeginQuery(GL_ANY_SAMPLES_PASSED, self.layer_query[0])
        self.draw_scene_pass(self.fbo_prepass, batches, 'PRE_PASS', self.default_shader['PRE_PASS'], UBOS, {}, textures, callbacks)
        glEndQuery(GL_ANY_SAMPLES_PASSED)

        #CUSTOM LIGHT SHADING
        self.custom_light_shading.load(self, self.t_depth, scene)
        callbacks.append(
            lambda shader : self.custom_light_shading.shader_callback(shader)
        )

        #MAIN-PASS
        textures = {
            'IN_NORMAL_DEPTH': self.t_prepass_normal_depth,
            'IN_ID': self.t_prepass_id,
            'IN_OPAQUE_COLOR': self.t_opaque_color,
            'IN_OPAQUE_DEPTH': self.t_opaque_depth,
            'IN_TRANSPARENT_DEPTH': self.t_transparent_depth,
            'IN_LAST_ID': self.t_last_layer_id,
        }
        clear_colors = [background_color]
        clear_colors.extend([(0)*4] * len(self.mesh_shader_custom_output_textures))
        self.fbo_main.clear(clear_colors)
        self.draw_scene_pass(self.fbo_main, batches, 'MAIN_PASS', self.default_shader['MAIN_PASS'], UBOS, {}, textures, callbacks)

        result = self.t_main_color

        graph = scene.world_parameters['Render Layer']
        if graph:
            IN = {
                'Color' : result,
                'Normal_Depth' : self.t_prepass_normal_depth,
                'ID' : self.t_prepass_id,
            } | self.mesh_shader_custom_output_textures
            OUT = { 'Color' : result }
            
            self.graphs['Render Layer'].run_source(self, graph['source'], graph['parameters'], IN, OUT)
            
            #TODO: AOV transparency ???
            if self.draw_layer_counter == 0:
                for key, fbo in self.render_layer_custom_output_accumulate_fbos.items():
                    if key in OUT and OUT[key]:
                        if internal_format_to_data_format(OUT[key].internal_format) == GL_FLOAT:
                            # TEMPORAL SUPER-SAMPLING ACCUMULATION
                            self.blend_texture(OUT[key], fbo, 1.0 / (self.sample_count + 1))
            result = OUT['Color']
        
        return result

PIPELINE = NPR_Pipeline
