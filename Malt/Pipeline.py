import math, os, ctypes
from os import path

from Malt.Utils import LOG

from Malt.GL.GL import *
from Malt.GL.Mesh import Mesh, MeshCustomLoad
from Malt.GL.Shader import Shader, UBO, shader_preprocessor

from Malt.Render import Common
from Malt.PipelineParameters import *

SHADER_DIR = path.join(path.dirname(__file__), 'Shaders')

class Pipeline():

    SHADER_INCLUDE_PATHS = []

    BLEND_SHADER = None
    COPY_SHADER = None

    def __init__(self, plugins=[]):
        from multiprocessing.dummy import Pool
        self.pool = Pool(16)

        if SHADER_DIR not in Pipeline.SHADER_INCLUDE_PATHS:
            Pipeline.SHADER_INCLUDE_PATHS.append(SHADER_DIR)

        self.resolution = None
        self.sample_count = 0
        self.result = None
        self.is_final_render = None
        
        plugins = [plugin for plugin in plugins if plugin.poll_pipeline(self)]
        self.setup_parameters()
        for plugin in plugins:
            plugin.register_pipeline_parameters(self.parameters)
        self.setup_graphs()
        for plugin in plugins:
            for graph in plugin.register_pipeline_graphs():
                self.add_graph(graph)
        for plugin in plugins:
            plugin.register_graph_libraries(self.graphs)
        for graph in self.graphs.values():
            graph.setup_reflection()
        self.setup_resources()
    
    def setup_parameters(self):
        self.parameters = PipelineParameters()
        
        self.parameters.mesh['double_sided'] = Parameter(False, Type.BOOL, doc=
            "Disables backface culling, so geometry is rendered from both sides.")
        
        self.parameters.mesh['precomputed_tangents'] = Parameter(False, Type.BOOL, doc="""
            Load precomputed mesh tangents *(needed for improving normal mapping quality on low poly meshes)*. 
            It's disabled by default since it slows down mesh loading in Blender.  
            When disabled, the *tangents* are calculated on the fly from the *pixel shader*.""")
        
        self.parameters.world['Material.Default'] = MaterialParameter('', '.mesh.glsl', 'Mesh', doc=
            "The default material, used for objects with no material assigned.")
        
        self.parameters.world['Material.Override'] = MaterialParameter('', '.mesh.glsl', 'Mesh', doc=
            "When set, overrides all scene materials with this one.")
        
        self.parameters.world['Viewport.Resolution Scale'] = Parameter(1.0 , Type.FLOAT, doc="""
            A multiplier for the viewport resolution.
            It can be lowered to improve viewport performance or for specific styles, like *pixel art*."""
        )
        self.parameters.world['Viewport.Smooth Interpolation'] = Parameter(True , Type.BOOL, doc="""
            The interpolation mode used when *Resolution Scale* is not 1.
            Toggles between *Nearest/Bilinear* interpolation.""")
    
    def get_parameters(self):
        return self.parameters

    def setup_graphs(self):
        self.graphs = {}
    
    def add_graph(self, graph):
        if graph.file_extension.endswith('glsl'):
            graph.include_paths += self.SHADER_INCLUDE_PATHS
        self.graphs[graph.name] = graph
    
    def get_graphs(self):
        result = {}
        for name, graph in self.graphs.items():
            result[name] = graph.get_serializable_copy()
        
        import copy
        group_graphs = {}
        for name, graph in result.items():
            if graph.language == 'GLSL':
                group_graphs[f'{name} group'] = copy.deepcopy(graph)
        
        for name, graph in group_graphs.items():
            graph.name = name
            from Malt.PipelineGraph import GLSLGraphIO
            io_types = [
                'bool','float','int','uint',
                'vec2','vec3','vec4',
                'ivec2','ivec3','ivec4',
                'uvec2','uvec3','uvec4',
                'mat4',
                'sampler1D','sampler2D',
            ]
            graph.graph_io={
                'NODE_GROUP_FUNCTION': GLSLGraphIO('NODE_GROUP_FUNCTION',
                    dynamic_input_types=io_types,
                    dynamic_output_types=io_types
                )
            }
            io = graph.graph_io['NODE_GROUP_FUNCTION']
            io.function = {
                'meta': {},
                'name': 'NODE_GROUP_FUNCTION',
                'type': 'void',
                'parameters': [],
            }
            io.signature = 'void NODE_GROUP_FUNCTION()'
            graph.default_graph_path = None
            graph.default_global_scope = ""
            graph.default_shader_src = ""

            graph.graph_type = graph.GLOBAL_GRAPH
        
        result.update(group_graphs)

        return result

    def setup_resources(self):
        self.common_buffer = Common.CommonBuffer()
        positions=[
             1.0,  1.0, 0.0,
             1.0, -1.0, 0.0,
            -1.0, -1.0, 0.0,
            -1.0,  1.0, 0.0,
        ]
        indices=[
            0, 1, 3,
            1, 2, 3,
        ]
        self.quad = Mesh(positions, indices)
        
        if Pipeline.BLEND_SHADER is None:
            source='''#include "Passes/BlendTexture.glsl"'''
            Pipeline.BLEND_SHADER = self.compile_shader_from_source(source)
        self.blend_shader = Pipeline.BLEND_SHADER

        if Pipeline.COPY_SHADER is None:
            source = '''#include "Passes/CopyTextures.glsl"'''
            Pipeline.COPY_SHADER = self.compile_shader_from_source(source)
        self.copy_shader = Pipeline.COPY_SHADER
    
    def get_render_outputs(self):
        return {
            'COLOR' : GL_RGBA32F,
            'DEPTH' : GL_R32F,
        }
    
    def get_samples(self):
        return [(0,0)]
    
    def needs_more_samples(self):
        return self.sample_count < len(self.get_samples())
    
    def setup_render_targets(self, resolution):
        pass
    
    def find_shader_path(self, path, search_paths=[]):
        if os.path.exists(path):
            return path
        else:
            for shader_path in self.SHADER_INCLUDE_PATHS + search_paths:
                full_path = os.path.join(shader_path, path)
                if os.path.exists(full_path):
                    return full_path
        return None
    
    def compile_shader_from_source(self, source, include_paths=[], defines=[]):
        vertex_src = shader_preprocessor(source, include_paths + self.SHADER_INCLUDE_PATHS, defines + ['VERTEX_SHADER'])
        pixel_src = shader_preprocessor(source, include_paths + self.SHADER_INCLUDE_PATHS, defines + ['PIXEL_SHADER'])
        return Shader(vertex_src, pixel_src)
            
    def compile_material_from_source(self, material_type, source, include_paths=[]):
        return self.graphs[material_type].compile_material(source, include_paths)
    
    def compile_material(self, shader_path, search_paths=[]):
        try:
            file_dir = path.dirname(shader_path)
            source = '#include "{}"'.format(path.basename(shader_path))
            material_type = shader_path.split('.')[-2]
            for graph in self.graphs.values():
                if shader_path.endswith(graph.file_extension):
                    material_type = graph.name
            return self.compile_material_from_source(material_type, source, [file_dir] + search_paths)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return str(e)
    
    def load_mesh(self, position, indices, normal, tangent=None, uvs=[], colors=[]):  
        # Each parameter implements the Malt.Utils.IBuffer interface
        # Indices is an array of index buffers corresponding to each of the materials a mesh has
        # VBOs are shared for all the materials
          
        def load_VBO(data):
            VBO = gl_buffer(GL_INT, 1)
            glGenBuffers(1, VBO)
            glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
            glBufferData(GL_ARRAY_BUFFER, data.size_in_bytes(), data.buffer(), GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            return VBO

        position_vbo = load_VBO(position)
        normal_vbo = load_VBO(normal)
        tangent_vbo = load_VBO(tangent) if tangent else None
        uv_vbos = [load_VBO(e) for e in uvs]
        color_vbos = [load_VBO(e) if e else None for e in colors]

        results = []

        for i, index in enumerate(indices):
            result = MeshCustomLoad()
            
            result.VAO = gl_buffer(GL_INT, 1)
            glGenVertexArrays(1, result.VAO)
            glBindVertexArray(result.VAO[0])
            
            result.EBO = gl_buffer(GL_INT, 1)
            glGenBuffers(1, result.EBO)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, result.EBO[0])
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, index.size_in_bytes(), index.buffer(), GL_STATIC_DRAW)
            
            result.index_count = len(index)

            result.position = position_vbo
            result.normal = normal_vbo
            result.tangent = tangent_vbo
            result.uvs = uv_vbos
            result.colors = color_vbos

            def bind_VBO(VBO, index, element_size, gl_type=GL_FLOAT, gl_normalize=GL_FALSE):
                glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
                glEnableVertexAttribArray(index)
                glVertexAttribPointer(index, element_size, gl_type, gl_normalize, 0, None)
            
            bind_VBO(result.position, 0, 3)
            if position.size_in_bytes() == normal.size_in_bytes():
                bind_VBO(result.normal, 1, 3)
            else:
                bind_VBO(result.normal, 1, 3, GL_SHORT, GL_TRUE)
            
            if tangent:
                bind_VBO(result.tangent, 2, 4)
            
            max_uv = 4
            max_vertex_colors = 4
            uv0_index = 3
            color0_index = uv0_index + max_uv
            for i, uv in enumerate(result.uvs):
                if i >= max_uv:
                    LOG.warning('{} : UV count exceeds max supported UVs ({})'.format(name, max_uv))
                    break
                bind_VBO(uv, uv0_index + i, 2)
            for i, color in enumerate(result.colors):
                if i >= max_vertex_colors:
                    LOG.warning('{} : Vertex Color Layer count exceeds max supported layers ({})'.format(name, max_uv))
                    break
                if color:
                    if colors[i]._ctype == ctypes.c_uint8:
                        bind_VBO(color, color0_index + i, 4, GL_UNSIGNED_BYTE, GL_TRUE)
                        result.color_is_srgb[i] = True
                    if colors[i]._ctype == ctypes.c_float:
                        bind_VBO(color, color0_index + i, 4, GL_FLOAT)

            glBindVertexArray(0)
            results.append(result)

        return results
    
    def draw_screen_pass(self, shader, target, blend = False):
        #Allow screen passes draw to gl_FragDepth
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_ALWAYS)
        glDisable(GL_CULL_FACE)
        if blend:
            glEnable(GL_BLEND)
        else:
            glDisable(GL_BLEND)
        target.bind()
        shader.bind()
        self.quad.draw()
    
    def blend_texture(self, blend_texture, target, opacity):
        self.blend_shader.textures['blend_texture'] = blend_texture
        glBlendFunc(GL_CONSTANT_ALPHA, GL_ONE_MINUS_CONSTANT_ALPHA)
        glBlendEquation(GL_FUNC_ADD)
        glBlendColor(0, 0, 0, opacity)
        self.draw_screen_pass(self.blend_shader, target, True)
    
    def copy_textures(self, target, color_sources=[], depth_source=None):
        for i, texture in enumerate(color_sources):
            self.copy_shader.textures[f'IN[{str(i)}]'] = texture
        self.copy_shader.textures['IN_DEPTH'] = depth_source
        self.draw_screen_pass(self.copy_shader, target)
    
    def build_scene_batches(self, objects):
        result = {}
        for obj in objects:
            if obj.material not in result:
                result[obj.material] = {}
            if obj.mesh not in result[obj.material]:
                result[obj.material][obj.mesh] = {}
            mesh_dict = result[obj.material][obj.mesh]
            if obj.mirror_scale:
                if 'mirror_scale' not in mesh_dict:
                    mesh_dict['mirror_scale'] = []
                mesh_dict['mirror_scale'].append(obj)
            else:
                if 'normal_scale' not in mesh_dict:
                    mesh_dict['normal_scale'] = []
                mesh_dict['normal_scale'].append(obj)
        
        # Assume at least 64kb of UBO storage (d3d11 requirement) and max element size of mat4
        max_instances = 1000
        models = (max_instances * (ctypes.c_float * 16))()
        ids = (max_instances * ctypes.c_uint)()

        for material, meshes in result.items():
            for mesh, scale_groups in meshes.items():
                for scale_group, objs in scale_groups.items():
                    batches = []
                    scale_groups[scale_group] = batches
                    
                    i = 0
                    batch_length = len(objs)
                    
                    while i < batch_length:
                        instance_i = i % max_instances
                        models[instance_i] = objs[i].matrix
                        ids[instance_i] = objs[i].parameters['ID']

                        i+=1
                        instances_count = instance_i + 1

                        if i == batch_length or instances_count == max_instances:
                            local_models = ((ctypes.c_float * 16) * instances_count).from_address(ctypes.addressof(models))
                            # IDs are stored as uvec4, so we make sure the buffer count is a multiple of 4,
                            # since some drivers will only bind a full uvec4 (see issue #319)
                            id_buffer_count = math.ceil(instances_count/4)*4
                            local_ids = (ctypes.c_uint * id_buffer_count).from_address(ctypes.addressof(ids))

                            models_UBO = UBO()
                            ids_UBO = UBO()

                            models_UBO.load_data(local_models)
                            ids_UBO.load_data(local_ids)

                            batches.append({
                                'instances_count': instances_count,
                                'BATCH_MODELS':models_UBO,
                                'BATCH_IDS':ids_UBO,
                            })
            
        return result
    
    def draw_scene_pass(self, render_target, scene_batches, pass_name=None, default_shader=None, shader_resources={}, depth_test_function=GL_LEQUAL):
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(depth_test_function)
        glDepthMask(GL_TRUE)
        glDepthRange(0,1)

        render_target.bind()

        _double_sided = None

        for material in scene_batches.keys():
            shader = default_shader
            if material and pass_name in material.shader and material.shader[pass_name]:
                shader = material.shader[pass_name]
            
            for resource in shader_resources.values():
                resource.shader_callback(shader)
            
            shader.bind()
            
            precomputed_tangents_uniform = shader.uniforms.get('PRECOMPUTED_TANGENTS')
            _precomputed_tangents = None
            _scale_group = None
            _color_is_srgb = None
            
            meshes = scene_batches[material]
            for mesh in meshes.keys():
                mesh.mesh.bind()
                
                double_sided = mesh.parameters['double_sided']
                if double_sided != _double_sided:
                    _double_sided = double_sided
                    if _double_sided:
                        glDisable(GL_CULL_FACE)
                    else:
                        glEnable(GL_CULL_FACE)
                        glCullFace(GL_BACK)
                
                color_is_srgb = tuple(mesh.mesh.color_is_srgb)
                if color_is_srgb != _color_is_srgb :
                    if 'COLOR_IS_SRGB' in shader.uniforms:
                        shader.uniforms['COLOR_IS_SRGB'].bind(color_is_srgb)
                        _color_is_srgb = color_is_srgb

                if precomputed_tangents_uniform:
                    precomputed_tangents = mesh.parameters['precomputed_tangents']
                    if _precomputed_tangents != precomputed_tangents:
                        _precomputed_tangents = precomputed_tangents
                        precomputed_tangents_uniform.bind(precomputed_tangents)

                for scale_group, batches in meshes[mesh].items():
                    if scale_group != _scale_group:
                        _scale_group = scale_group
                        if scale_group == 'normal_scale':
                            glFrontFace(GL_CCW)
                            if 'MIRROR_SCALE' in shader.uniforms:
                                shader.uniforms['MIRROR_SCALE'].bind(False)
                        else:
                            glFrontFace(GL_CW)
                            if 'MIRROR_SCALE' in shader.uniforms:
                                shader.uniforms['MIRROR_SCALE'].bind(True)
                
                    for batch in batches:
                        batch['BATCH_MODELS'].bind(shader.uniform_blocks['BATCH_MODELS'])
                        batch['BATCH_IDS'].bind(shader.uniform_blocks['BATCH_IDS'])
                        glDrawElementsInstanced(GL_TRIANGLES, mesh.mesh.index_count, GL_UNSIGNED_INT, NULL, batch['instances_count'])


    def render(self, resolution, scene, is_final_render, is_new_frame):
        self.is_final_render = is_final_render
        if self.resolution != resolution:
            self.resolution = resolution
            self.setup_render_targets(resolution)
            self.sample_count = 0
        
        if is_new_frame:
            self.sample_count = 0
        
        if self.needs_more_samples() == False:
            return self.result
        
        self.common_buffer.load(scene, resolution)
        self.result = self.do_render(resolution, scene, is_final_render, is_new_frame)
        
        self.sample_count += 1

        return self.result

    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        return {}

