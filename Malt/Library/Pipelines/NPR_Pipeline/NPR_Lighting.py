# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

from Malt.GL.GL import *
from Malt.GL.Shader import UBO
from Malt.GL.Texture import TextureArray, CubeMapArray
from Malt.GL.RenderTarget import ArrayLayerTarget, RenderTarget

from Malt.PipelineParameters import Parameter, Type

from Malt.Library.Render import Common
from Malt.Library.Render import Lighting

class NPR_Lighting():

    def __init__(self, parameters):
        parameters.world['ShadowMaps.Sun.Cascades.Distribution Scalar'] = Parameter(0.9, Type.FLOAT)
        parameters.world['ShadowMaps.Sun.Cascades.Count'] = Parameter(4, Type.INT)
        parameters.world['ShadowMaps.Sun.Cascades.Count @ Preview'] = Parameter(2, Type.INT)
        parameters.world['ShadowMaps.Sun.Cascades.Max Distance'] = Parameter(100, Type.FLOAT)
        parameters.world['ShadowMaps.Sun.Cascades.Max Distance @ Preview'] = Parameter(25, Type.FLOAT)
        parameters.world['ShadowMaps.Sun.Resolution'] = Parameter(2048, Type.INT)
        parameters.world['ShadowMaps.Spot.Resolution'] = Parameter(2048, Type.INT)
        parameters.world['ShadowMaps.Spot.Resolution @ Preview'] = Parameter(512, Type.INT)
        parameters.world['ShadowMaps.Point.Resolution'] = Parameter(2048, Type.INT)
        parameters.world['ShadowMaps.Point.Resolution @ Preview'] = Parameter(512, Type.INT)
        parameters.light['Light Group'] = Parameter(1, Type.INT)
        parameters.material['Light Groups.Light'] = Parameter([1,0,0,0], Type.INT, 4, 'mesh')
        parameters.material['Light Groups.Shadow'] = Parameter([1,0,0,0], Type.INT, 4, 'mesh')
        self.lights_buffer = Lighting.get_lights_buffer()
        self.light_groups_buffer = NPR_LightsGroupsBuffer()
        self.shadowmaps_opaque, self.shadowmaps_transparent = get_shadow_maps()
        self.common_buffer = Common.CommonBuffer()
    
    def load(self, pipeline, scene, opaque_batches, transparent_batches, sample_offset, sample_count):
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

        def render_shadowmaps(lights, fbos_opaque, fbos_transparent, sample_offset = sample_offset):
            for light_index, light_matrices_pair in enumerate(lights.items()):
                light, matrices = light_matrices_pair
                for matrix_index, camera_projection_pair in enumerate(matrices): 
                    camera, projection = camera_projection_pair
                    i = light_index * len(matrices) + matrix_index
                    self.common_buffer.load(scene, fbos_opaque[i].resolution, sample_offset, sample_count, camera, projection)
                    def get_light_group_batches(batches):
                        result = {}
                        for material, meshes in batches.items():
                            if material and light.parameters['Light Group'] in material.parameters['Light Groups.Shadow']:
                                result[material] = meshes
                        return result
                    #TODO: Callback
                    pipeline.draw_scene_pass(fbos_opaque[i], get_light_group_batches(opaque_batches), 
                        'SHADOW_PASS', pipeline.default_shader['SHADOW_PASS'], UBOS)
                    pipeline.draw_scene_pass(fbos_transparent[i], get_light_group_batches(transparent_batches), 
                        'SHADOW_PASS', pipeline.default_shader['SHADOW_PASS'], UBOS)
        
        render_shadowmaps(self.lights_buffer.spots,
            self.shadowmaps_opaque.spot_fbos, self.shadowmaps_transparent.spot_fbos)
        
        glEnable(GL_DEPTH_CLAMP)
        render_shadowmaps(self.lights_buffer.suns,
            self.shadowmaps_opaque.sun_fbos, self.shadowmaps_transparent.sun_fbos)
        glDisable(GL_DEPTH_CLAMP)

        render_shadowmaps(self.lights_buffer.points,
            self.shadowmaps_opaque.point_fbos, self.shadowmaps_transparent.point_fbos, (0,0))
    
    def shader_callback(self, shader):
        if 'SCENE_LIGHTS' in shader.uniform_blocks:
            self.lights_buffer.bind(shader.uniform_blocks['SCENE_LIGHTS'])
        self.light_groups_buffer.shader_callback(shader)
        self.shadowmaps_opaque.shader_callback(shader)
        self.shadowmaps_transparent.shader_callback(shader)


_SHADOWMAPS = None

def get_shadow_maps():
    global _SHADOWMAPS
    if _SHADOWMAPS is None: _SHADOWMAPS = (NPR_ShadowMaps(), NPR_TransparentShadowMaps())
    return _SHADOWMAPS

class C_NPR_LightGroupsBuffer(ctypes.Structure):
    _fields_ = [
        ('light_group_index', ctypes.c_int*Lighting.MAX_LIGHTS),
    ]

class NPR_LightsGroupsBuffer():

    def __init__(self):
        self.data = C_NPR_LightGroupsBuffer()
        self.UBO = UBO()
    
    def load(self, scene):
        for i, light in enumerate(scene.lights):
            self.data.light_group_index[i] = light.parameters['Light Group']

        self.UBO.load_data(self.data)

        for material in scene.materials:
            for shader in material.shader.values():
                if 'MATERIAL_LIGHT_GROUPS' in shader.uniforms.keys():
                    shader.uniforms['MATERIAL_LIGHT_GROUPS'].set_value(material.parameters['Light Groups.Light'])

    def shader_callback(self, shader):
        if 'LIGHT_GROUPS' in shader.uniform_blocks:
            self.UBO.bind(shader.uniform_blocks['LIGHT_GROUPS'])
        

class NPR_ShadowMaps(Lighting.ShadowMaps):

    def __init__(self):
        super().__init__()
        self.spot_id_t = None
        self.sun_id_t = None
        self.point_id_t = None
    
    def setup(self, create_fbos=True):
        super().setup(False)
        self.spot_id_t = TextureArray((self.spot_resolution, self.spot_resolution), self.max_spots, 
            GL_R16UI, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        self.sun_id_t = TextureArray((self.sun_resolution, self.sun_resolution), self.max_suns, 
            GL_R16UI, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        self.point_id_t = CubeMapArray((self.point_resolution, self.point_resolution), self.max_points, 
            GL_R16UI, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        
        if create_fbos:
            self.spot_fbos = []
            for i in range(self.spot_depth_t.length):
                self.spot_fbos.append(RenderTarget([ArrayLayerTarget(self.spot_id_t, i)], ArrayLayerTarget(self.spot_depth_t, i)))

            self.sun_fbos = []
            for i in range(self.sun_depth_t.length):
                self.sun_fbos.append(RenderTarget([ArrayLayerTarget(self.sun_id_t, i)], ArrayLayerTarget(self.sun_depth_t, i)))
            
            self.point_fbos = []
            for i in range(self.point_depth_t.length*6):
                self.point_fbos.append(RenderTarget([ArrayLayerTarget(self.point_id_t, i)], ArrayLayerTarget(self.point_depth_t, i)))
    
    def clear(self, spot_count, sun_count, point_count):
        for i in range(spot_count):
            self.spot_fbos[i].clear([0], depth=1)
        for i in range(sun_count):
            self.sun_fbos[i].clear([0], depth=1)
        for i in range(point_count*6):
            self.point_fbos[i].clear([0], depth=1)
    
    def shader_callback(self, shader):
        super().shader_callback(shader)
        shader.textures['SHADOWMAPS_ID_SPOT'] = self.spot_id_t
        shader.textures['SHADOWMAPS_ID_SUN'] = self.sun_id_t
        shader.textures['SHADOWMAPS_ID_POINT'] = self.point_id_t

class NPR_TransparentShadowMaps(NPR_ShadowMaps):

    def __init__(self):
        super().__init__()
        self.spot_color_t = None
        self.sun_color_t = None
        self.point_color_t = None
    
    def setup(self, create_fbos=True):
        super().setup(False)
        self.spot_color_t = TextureArray((self.spot_resolution, self.spot_resolution), self.max_spots, GL_RGB8)
        self.sun_color_t = TextureArray((self.sun_resolution, self.sun_resolution), self.max_suns, GL_RGB8)
        self.point_color_t = CubeMapArray((self.point_resolution, self.point_resolution), self.max_points, GL_RGB8)
        
        if create_fbos:
            self.spot_fbos = []
            for i in range(self.spot_depth_t.length):
                targets = [ArrayLayerTarget(self.spot_id_t, i), ArrayLayerTarget(self.spot_color_t, i)]
                self.spot_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.spot_depth_t, i)))

            self.sun_fbos = []
            for i in range(self.sun_depth_t.length):
                targets = [ArrayLayerTarget(self.sun_id_t, i), ArrayLayerTarget(self.sun_color_t, i)]
                self.sun_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.sun_depth_t, i)))
            
            self.point_fbos = []
            for i in range(self.point_depth_t.length*6):
                targets = [ArrayLayerTarget(self.point_id_t, i), ArrayLayerTarget(self.point_color_t, i)]
                self.point_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.point_depth_t, i)))
    
    def clear(self, spot_count, sun_count, point_count):
        for i in range(spot_count):
            self.spot_fbos[i].clear([0, (0,0,0,0)], depth=1)
        for i in range(sun_count):
            self.sun_fbos[i].clear([0, (0,0,0,0)], depth=1)
        for i in range(point_count*6):
            self.point_fbos[i].clear([0, (0,0,0,0)], depth=1)

    def shader_callback(self, shader):
        shader.textures['TRANSPARENT_SHADOWMAPS_DEPTH_SPOT'] = self.spot_depth_t
        shader.textures['TRANSPARENT_SHADOWMAPS_DEPTH_SUN'] = self.sun_depth_t
        shader.textures['TRANSPARENT_SHADOWMAPS_DEPTH_POINT'] = self.point_depth_t
        shader.textures['TRANSPARENT_SHADOWMAPS_ID_SPOT'] = self.spot_id_t
        shader.textures['TRANSPARENT_SHADOWMAPS_ID_SUN'] = self.sun_id_t
        shader.textures['TRANSPARENT_SHADOWMAPS_ID_POINT'] = self.point_id_t
        shader.textures['TRANSPARENT_SHADOWMAPS_COLOR_SPOT'] = self.spot_color_t
        shader.textures['TRANSPARENT_SHADOWMAPS_COLOR_SUN'] = self.sun_color_t
        shader.textures['TRANSPARENT_SHADOWMAPS_COLOR_POINT'] = self.point_color_t
        

