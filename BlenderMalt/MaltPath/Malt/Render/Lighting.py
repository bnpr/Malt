# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import math
import ctypes
import copy

import pyrr

from Malt.GL import *
from Malt.UBO import UBO
from Malt.Texture import TextureArray, CubeMapArray
from Malt.RenderTarget import ArrayLayerTarget, RenderTarget
from Malt.Render import Common


LIGHT_SUN = 1
LIGHT_POINT = 2
LIGHT_SPOT = 3

class C_Light(ctypes.Structure):
    _fields_ = [
        ('color', ctypes.c_float*3),
        ('type', ctypes.c_int32),
        ('position', ctypes.c_float*3),
        ('radius', ctypes.c_float),
        ('direction', ctypes.c_float*3),
        ('spot_angle', ctypes.c_float),
        ('spot_blend', ctypes.c_float),
        ('type_index', ctypes.c_int32),
        ('__padding', ctypes.c_int32*2),
    ]


#TODO: Hard-coded for Blender conventions for now
def make_projection_matrix(fov, aspect_ratio, near, far):
    x_scale = 1.0 / math.tan(fov / 2.0)
    y_scale = x_scale * aspect_ratio
    return pyrr.Matrix44([
        x_scale, 0, 0, 0,
        0, y_scale, 0, 0,
        0, 0, (-(far + near)) / (far - near), -1,
        0, 0, (-2.0 * far * near) / (far - near), 0
    ])

MAX_SPOTS = 64
MAX_SUNS = 8
SUN_CASCADES = 6

class C_LightsBuffer(ctypes.Structure):
    
    _fields_ = [
        ('lights', C_Light*128),
        ('lights_count', ctypes.c_int),
        ('__padding', ctypes.c_int32*3),
        ('spot_matrices', ctypes.c_float*16*MAX_SPOTS),
        ('sun_matrices', ctypes.c_float*16*(MAX_SUNS*SUN_CASCADES)),
    ]


class ShadowMaps(object):

    def __init__(self):
        self.max_spots = 1
        self.spot_resolution = 2048

        self.spot_depth_t = None
        self.spot_id_t = None
        self.spot_fbos = []

        self.sun_cascades = SUN_CASCADES
        self.max_suns = 1
        self.sun_resolution = 2048
        
        self.sun_depth_t = None
        self.sun_id_t = None
        self.sun_fbos = []

        self.max_points = 1
        self.point_resolution = 512

        self.point_depth_t = None
        self.point_id_t = None
        self.point_fbos = []

        self.draw_ids = True

        self.initialized = False

    def setup(self):
        self.spot_depth_t = TextureArray((self.spot_resolution, self.spot_resolution), self.max_spots, GL_DEPTH_COMPONENT32F)
        if self.draw_ids:
            self.spot_id_t = TextureArray((self.spot_resolution, self.spot_resolution), self.max_spots, GL_R32F)
        self.spot_fbos = []
        for i in range(self.spot_depth_t.length):
            targets = [None, ArrayLayerTarget(self.spot_id_t, i)] if self.draw_ids else [None, None] 
            self.spot_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.spot_depth_t, i)))

        self.sun_depth_t = TextureArray((self.sun_resolution, self.sun_resolution), self.max_suns * self.sun_cascades, GL_DEPTH_COMPONENT32F)
        if self.draw_ids:
            self.sun_id_t = TextureArray((self.sun_resolution, self.sun_resolution), self.max_suns * self.sun_cascades, GL_R32F)
        self.sun_fbos = []
        for i in range(self.sun_depth_t.length):
            targets = [None, ArrayLayerTarget(self.sun_id_t, i)] if self.draw_ids else [None, None]
            self.sun_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.sun_depth_t, i)))
        
        self.point_depth_t = CubeMapArray((self.point_resolution, self.point_resolution), self.max_points, GL_DEPTH_COMPONENT32F)
        if self.draw_ids:
            self.point_id_t = CubeMapArray((self.point_resolution, self.point_resolution), self.max_points, GL_R32F)
        self.point_fbos = []
        for i in range(self.point_depth_t.length*6):
            targets = [None, ArrayLayerTarget(self.point_id_t, i)] if self.draw_ids else [None, None]
            self.point_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.point_depth_t, i)))
        
        self.initialized = True

    def load(self, scene, spot_resolution, sun_resolution, point_resolution):
        needs_setup = self.initialized is False
        
        new_settings = (spot_resolution, sun_resolution, point_resolution)
        current_settings = (self.spot_resolution, self.sun_resolution, self.point_resolution)
        if new_settings != current_settings:
            self.spot_resolution = spot_resolution
            self.sun_resolution = sun_resolution
            self.point_resolution = point_resolution
            needs_setup = True
        
        spot_lights = len([l for l in scene.lights if l.type == LIGHT_SPOT])
        if spot_lights > self.max_spots:
            self.max_spots = spot_lights
            needs_setup = True
        
        sun_lights = len([l for l in scene.lights if l.type == LIGHT_SUN])
        if sun_lights > self.max_suns:
            self.max_suns = sun_lights
            needs_setup = True 

        point_lights = len([l for l in scene.lights if l.type == LIGHT_POINT])
        if point_lights > self.max_points:
            self.max_points = point_lights
            needs_setup = True
        
        if needs_setup:
            self.setup()


class LightsBuffer(object):
    
    def __init__(self):
        self.data = C_LightsBuffer()
        self.UBO = UBO()
        self.shadowmaps = ShadowMaps()
        self.common_buffer = Common.CommonBuffer()
    
    def load(self, scene, pipeline, pass_name, cascades_distribution_exponent, 
        spot_resolution = 2048, sun_resolution = 2048, point_resolution = 512):
        #TODO: Automatic distribution exponent based on FOV

        scene = copy.copy(scene)
        real_scene_camera = scene.camera
        scene.camera = copy.deepcopy(scene.camera)
        self.shadowmaps.load(scene, spot_resolution, sun_resolution, point_resolution)
        UBOS = {
            'COMMON_UNIFORMS' : self.common_buffer
        }
        spot_count = 0
        sun_count = 0
        point_count = 0

        for i, light in enumerate(scene.lights):
            self.data.lights[i].color = light.color
            self.data.lights[i].type = light.type
            self.data.lights[i].position = light.position
            self.data.lights[i].radius = light.radius
            self.data.lights[i].direction = light.direction
            self.data.lights[i].spot_angle = light.spot_angle
            self.data.lights[i].spot_blend = light.spot_blend

            if light.type == LIGHT_SPOT:
                self.data.lights[i].type_index = spot_count

                camera_matrix = pyrr.Matrix44(light.matrix)
                
                projection_matrix = make_projection_matrix(light.spot_angle,1,0.01,light.radius)
                spot_matrix = projection_matrix * camera_matrix
                
                self.data.spot_matrices[spot_count] = tuple([e for vector in spot_matrix for e in vector])

                scene.camera.camera_matrix = light.matrix
                scene.camera.projection_matrix = tuple([e for vector in projection_matrix for e in vector])
                
                offset = pipeline.get_samples()[pipeline.sample_count]
                spot_resolution = self.shadowmaps.spot_resolution
                self.common_buffer.load(scene, (spot_resolution, spot_resolution), offset, pipeline.sample_count)

                self.shadowmaps.spot_fbos[spot_count].clear(depth=1)
                pipeline.draw_scene_pass(self.shadowmaps.spot_fbos[spot_count], 
                    scene.objects, pass_name, pipeline.default_shader[pass_name], UBOS)

                spot_count+=1
            
            if light.type == LIGHT_SUN:
                self.data.lights[i].type_index = sun_count

                sun_matrix = pyrr.Matrix44(light.matrix)
                projection_matrix = pyrr.Matrix44(real_scene_camera.projection_matrix)
                view_matrix = projection_matrix * pyrr.Matrix44(real_scene_camera.camera_matrix)

                sun_cascades = self.shadowmaps.sun_cascades
                sun_resolution = self.shadowmaps.sun_resolution
                cascades_matrices = get_sun_cascades(sun_matrix, projection_matrix, view_matrix, sun_cascades, cascades_distribution_exponent)
                
                for i, cascade in enumerate(cascades_matrices):
                    cascade = tuple([e for vector in cascade for e in vector])
                    
                    scene.camera.camera_matrix = cascade
                    scene.camera.projection_matrix = tuple([e for vector in pyrr.Matrix44.identity() for e in vector])

                    self.data.sun_matrices[sun_count * sun_cascades + i] = cascade
                
                    offset = pipeline.get_samples()[pipeline.sample_count]
                    self.common_buffer.load(scene, (sun_resolution, sun_resolution), offset, pipeline.sample_count)

                    fbo = self.shadowmaps.sun_fbos[sun_count * sun_cascades + i]
                    fbo.clear(depth=1)
                    glEnable(GL_DEPTH_CLAMP)
                    pipeline.draw_scene_pass(fbo, scene.objects, pass_name, pipeline.default_shader[pass_name], UBOS)
                    glDisable(GL_DEPTH_CLAMP)

                sun_count+=1
            
            if light.type == LIGHT_POINT:
                self.data.lights[i].type_index = point_count

                cube_map_axes = [
                    (( 1, 0, 0),( 0,-1, 0)),
                    ((-1, 0, 0),( 0,-1, 0)),
                    (( 0, 1, 0),( 0, 0, 1)),
                    (( 0,-1, 0),( 0, 0,-1)),
                    (( 0, 0, 1),( 0,-1, 0)),
                    (( 0, 0,-1),( 0,-1, 0))
                ]
                matrices = []
                for axes in cube_map_axes:
                    position = pyrr.Vector3(light.position)
                    front = pyrr.Vector3(axes[0])
                    up = pyrr.Vector3(axes[1])
                    matrices.append(pyrr.Matrix44.look_at(position, position + front, up))

                projection_matrix = make_projection_matrix(math.pi / 2.0, 1.0, 0.01, light.radius)

                for i in range(6):
                    scene.camera.camera_matrix = tuple([e for vector in matrices[i] for e in vector])
                    scene.camera.projection_matrix = tuple([e for vector in projection_matrix for e in vector])

                    offset = pipeline.get_samples()[pipeline.sample_count]
                    offset = (0,0)
                    point_resolution = self.shadowmaps.point_resolution
                    self.common_buffer.load(scene, (point_resolution, point_resolution), offset, pipeline.sample_count)
                    
                    fbo = self.shadowmaps.point_fbos[point_count * 6 + i]
                    fbo.clear(depth=1)
                    pipeline.draw_scene_pass(fbo, scene.objects, pass_name, pipeline.default_shader[pass_name], UBOS)
                
                point_count+=1
            
            
        self.data.lights_count = len(scene.lights)
        
        self.UBO.load_data(self.data)
    
    def bind(self, location):
        self.UBO.bind(location)

    def shader_callback(self, shader):
        shader.textures['SPOT_SHADOWMAPS'] = self.shadowmaps.spot_depth_t
        shader.textures['SUN_SHADOWMAPS'] = self.shadowmaps.sun_depth_t
        shader.textures['POINT_SHADOWMAPS'] = self.shadowmaps.point_depth_t
        shader.textures['SPOT_ID_MAPS'] = self.shadowmaps.spot_id_t
        shader.textures['SUN_ID_MAPS'] = self.shadowmaps.sun_id_t
        shader.textures['POINT_ID_MAPS'] = self.shadowmaps.point_id_t


def get_sun_cascades(sun_from_world_matrix, projection_matrix, view_from_world_matrix, cascades_count, cascades_distribution_exponent):
    cascades = []
    splits = []
    
    #if is ortho
    if projection_matrix[3][3] == 1.0:
        for i in range(cascades_count):
            split = -1.0 + (2.0 / cascades_count) * (i+1)
            splits.append(split)
    #is perspective
    else:
        clip_end = projection_matrix.inverse * pyrr.Vector4([0,0,1,1])
        clip_end /= clip_end.w
        clip_end = -clip_end.z
        
        step_size = clip_end / cascades_count
        for i in range(cascades_count):
            split = (i+1) * step_size
            projected = projection_matrix * pyrr.Vector4([0,0,-split,1])
            projected = (projected / projected.w) * (1.0 if projected.w >= 0 else -1.0)
            depth = projected.z
            #normalize depth (0,1)
            depth = depth * 0.5 + 0.5
            #make steps less linear
            depth = depth ** cascades_distribution_exponent
            #back to (-1,+1) range
            depth = depth * 2.0 - 1.0
            splits.append(depth)
        
    for i in range(len(splits)):
        near = -1
        if i > 0:
            near = splits[i-1]
        far = splits[i]
        cascades.append(sun_shadowmap_matrix(sun_from_world_matrix, view_from_world_matrix, near, far))
    
    return cascades


def frustum_corners(view_from_world_matrix, near, far):
    m = view_from_world_matrix.inverse
    corners = []

    for x in (-1, 1):
        for y in (-1, 1):
            for z in (near, far):
                v = pyrr.Vector4([x, y, z, 1])
                v = m * v
                v /= v.w
                corners.append(v)
    
    return corners

def sun_shadowmap_matrix(sun_from_world_matrix, view_from_world_matrix, near, far):
    INFINITY = float('inf')
    aabb = {
        'min': pyrr.Vector3([ INFINITY,  INFINITY,  INFINITY]),
        'max': pyrr.Vector3([-INFINITY, -INFINITY, -INFINITY])
    }
    
    for corner in frustum_corners(view_from_world_matrix, near, far):
        corner = sun_from_world_matrix * corner
        aabb['min'].x = min(aabb['min'].x, corner.x)
        aabb['min'].y = min(aabb['min'].y, corner.y)
        aabb['min'].z = min(aabb['min'].z, corner.z)
        aabb['max'].x = max(aabb['max'].x, corner.x)
        aabb['max'].y = max(aabb['max'].y, corner.y)
        aabb['max'].z = max(aabb['max'].z, corner.z)

    world_from_light_space = sun_from_world_matrix.inverse

    size = aabb['max'] - aabb['min']
    aabb['min'] = world_from_light_space * pyrr.Vector4([*aabb['min'].tolist(), 1.0])
    aabb['max'] = world_from_light_space * pyrr.Vector4([*aabb['max'].tolist(), 1.0])
    center = (aabb['min'] + aabb['max']) / 2.0
    center = pyrr.Vector3(center.tolist()[:3])

    scale = pyrr.Matrix44.from_scale(size)
    translate = pyrr.Matrix44.from_translation(center)
    
    matrix = translate * world_from_light_space * scale

    screen = pyrr.Matrix44([
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0,-1, 0,
        0, 0, 0, 1
    ])

    return screen * matrix.inverse

