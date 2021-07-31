# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import os
from os import path
import ctypes

from Malt.GL.GL import *
from Malt.GL.Mesh import Mesh
from Malt.GL.Shader import Shader, UBO, shader_preprocessor

from Malt.Parameter import *

#Workaround for handling multiple OpenGL contexts
MAIN_CONTEXT = True

SHADER_DIR = path.join(path.dirname(__file__), 'Shaders')

class Pipeline(object):

    GLSL_HEADER = "#version 410 core\n"

    SHADER_INCLUDE_PATHS = []

    BLEND_SHADER = None
    COPY_SHADER = None

    def __init__(self):
        from multiprocessing.dummy import Pool
        self.pool = Pool(16)

        self.parameters = PipelineParameters()
        self.parameters.mesh['double_sided'] = Parameter(False, Type.BOOL)
        self.parameters.mesh['precomputed_tangents'] = Parameter(False, Type.BOOL)

        self.graphs = {}

        if SHADER_DIR not in Pipeline.SHADER_INCLUDE_PATHS:
            Pipeline.SHADER_INCLUDE_PATHS.append(SHADER_DIR)

        self.resolution = None
        self.sample_count = 0

        self.result = None

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
        
        self.default_shader = None

    def get_parameters(self):
        return self.parameters
    
    def get_graphs(self):
        result = {}
        for name, graph in self.graphs.items():
            result[name] = graph.get_serializable_copy()
        return result
    
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
    
    def preprocess_shader_from_source(self, shader_source, include_paths=[], defines=[]):
        return self.preprocess_shaders_from_source(shader_source, include_paths, [defines])[0]
    
    def preprocess_shaders_from_source(self, shader_source, include_paths=[], defines_lists=[]):
        shader_source = Pipeline.GLSL_HEADER + shader_source
        include_paths = include_paths + Pipeline.SHADER_INCLUDE_PATHS

        def preprocess(params):
            return shader_preprocessor(*params)
        
        params = []
        for defines in defines_lists:
            params.append((shader_source, include_paths, defines))

        return self.pool.map(preprocess, params)
    
    def compile_shader_from_source(self, shader_source, include_paths=[], defines=[]):
        return self.compile_shaders_from_source(shader_source, include_paths, {'shader': defines})['shader']
        
    def compile_shaders_from_source(self, shader_source, include_paths=[], shader_defines_map={}):
        defines_lists = []
        for defines in shader_defines_map.values():
            defines_lists.append(['VERTEX_SHADER']+defines) 
            defines_lists.append(['PIXEL_SHADER']+defines) 
        preprocessed_sources = self.preprocess_shaders_from_source(shader_source, include_paths, defines_lists)
        
        results = {}
        for shader in shader_defines_map:
            vertex = preprocessed_sources.pop(0)
            pixel = preprocessed_sources.pop(0)
            results[shader] = Shader(vertex, pixel)
        return results
    
    def compile_material_from_source(self, material_type, source, include_paths=[]):
        return {}
    
    def compile_material(self, shader_path, search_paths=[]):
        try:
            file_dir = path.dirname(shader_path)
            material_type = shader_path.split('.')[-2]
            source = '#include "{}"'.format(path.basename(shader_path))
            return self.compile_material_from_source(material_type, source, [file_dir] + search_paths)
        except:
            import traceback
            return traceback.format_exc()
    
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
            self.copy_shader.textures['IN_'+str(i)] = texture
        self.copy_shader.textures['IN_DEPTH'] = depth_source
        self.draw_screen_pass(self.copy_shader, target)
    
    def build_scene_batches(self, objects):
        result = {}
        for obj in objects:
            if obj.material not in result:
                result[obj.material] = {}
            if obj.mesh not in result[obj.material]:
                result[obj.material][obj.mesh] = {
                    'normal_scale':[],
                    'mirror_scale':[],
                }
            if obj.mirror_scale:
                result[obj.material][obj.mesh]['mirror_scale'].append(obj)
            else:
                result[obj.material][obj.mesh]['normal_scale'].append(obj)
        
        # Assume at least 64kb of UBO storage (d3d11 requirement) and max element size of mat4
        max_instances = 1000
        models = (max_instances * (ctypes.c_float * 16))()
        ids = (max_instances * ctypes.c_float)()

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
                            local_ids = (ctypes.c_float * instances_count).from_address(ctypes.addressof(ids))

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
    
    def draw_scene_pass(self, render_target, batches, pass_name=None, default_shader=None, uniform_blocks={}, uniforms={}, textures={}, shader_callbacks=[]):
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glDepthMask(GL_TRUE)
        glDepthRange(0,1)

        render_target.bind()

        for material, meshes in batches.items():
            shader = default_shader
            if material and pass_name in material.shader and material.shader[pass_name]:
                shader = material.shader[pass_name]
            
            for name, uniform in uniforms.items():
                if name in shader.uniforms:
                    shader.uniforms[name].set_value(uniform)
            
            for name, texture in textures.items():
                if name in shader.textures:
                    shader.textures[name] = texture
            
            for callback in shader_callbacks:
                callback(shader)
            
            shader.bind()

            for name, block in uniform_blocks.items():
                if name in shader.uniform_blocks:
                    block.bind(shader.uniform_blocks[name])

            for mesh, scale_groups in meshes.items():

                mesh.mesh.bind()
                
                for scale_group, batches in scale_groups.items():
                    if mesh.parameters['double_sided']:
                        glDisable(GL_CULL_FACE)
                    else:
                        glEnable(GL_CULL_FACE)
                        glCullFace(GL_BACK)  
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
        if self.resolution != resolution:
            self.resolution = resolution
            self.setup_render_targets(resolution)
            self.sample_count = 0
        
        if is_new_frame:
            self.sample_count = 0
        
        if self.needs_more_samples() == False:
            return self.result
        
        self.result = self.do_render(resolution, scene, is_final_render, is_new_frame)
        
        self.sample_count += 1

        return self.result

    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        return {}

