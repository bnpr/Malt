# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import math
import ctypes

import pyrr

from Malt.GL.GL import *
from Malt.GL.Shader import UBO
from Malt.GL.Texture import TextureArray, CubeMapArray
from Malt.GL.RenderTarget import ArrayLayerTarget, RenderTarget

from Malt import Pipeline

_LIGHTS_BUFFER = None

def get_lights_buffer():
    if Pipeline.MAIN_CONTEXT:
        global _LIGHTS_BUFFER
        if _LIGHTS_BUFFER is None: _LIGHTS_BUFFER = LightsBuffer()
        return _LIGHTS_BUFFER
    else:
        return LightsBuffer()

_SHADOWMAPS = None

def get_shadow_maps():
    if Pipeline.MAIN_CONTEXT:
        global _SHADOWMAPS
        if _SHADOWMAPS is None: _SHADOWMAPS = ShadowMaps()
        return _SHADOWMAPS
    else:
        return ShadowMaps()

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

MAX_SPOTS = 64
MAX_SUNS = 64

MAX_LIGHTS = 128

class C_LightsBuffer(ctypes.Structure):
    
    _fields_ = [
        ('lights', C_Light*MAX_LIGHTS),
        ('lights_count', ctypes.c_int),
        ('cascades_count', ctypes.c_int),
        ('__padding', ctypes.c_int32*2),
        ('spot_matrices', ctypes.c_float*16*MAX_SPOTS),
        ('sun_matrices', ctypes.c_float*16*MAX_SUNS),
    ]

class ShadowMaps(object):

    def __init__(self):
        self.max_spots = 1
        self.spot_resolution = 2048

        self.spot_depth_t = None
        self.spot_fbos = []

        self.max_suns = 1
        self.sun_resolution = 2048
        
        self.sun_depth_t = None
        self.sun_fbos = []

        self.max_points = 1
        self.point_resolution = 512

        self.point_depth_t = None
        self.point_fbos = []

        self.initialized = False

    def load(self, scene, spot_resolution, sun_resolution, point_resolution, sun_cascades):
        needs_setup = self.initialized is False
        self.initialized = True
        
        new_settings = (spot_resolution, sun_resolution, point_resolution)
        current_settings = (self.spot_resolution, self.sun_resolution, self.point_resolution)
        if new_settings != current_settings:
            self.spot_resolution = spot_resolution
            self.sun_resolution = sun_resolution
            self.point_resolution = point_resolution
            needs_setup = True
        
        spot_count = len([l for l in scene.lights if l.type == LIGHT_SPOT])
        if spot_count > self.max_spots:
            self.max_spots = spot_count
            needs_setup = True
        
        sun_count = len([l for l in scene.lights if l.type == LIGHT_SUN])
        sun_count  = sun_count * sun_cascades
        if sun_count > self.max_suns:
            self.max_suns = sun_count
            needs_setup = True 

        point_count = len([l for l in scene.lights if l.type == LIGHT_POINT])
        if point_count > self.max_points:
            self.max_points = point_count
            needs_setup = True
        
        if needs_setup:
            self.setup()
        
        self.clear(spot_count, sun_count, point_count)
    
    def setup(self, create_fbos=True):
        self.spot_depth_t = TextureArray((self.spot_resolution, self.spot_resolution), self.max_spots, GL_DEPTH_COMPONENT32F)
        self.sun_depth_t = TextureArray((self.sun_resolution, self.sun_resolution), self.max_suns, GL_DEPTH_COMPONENT32F)
        self.point_depth_t = CubeMapArray((self.point_resolution, self.point_resolution), self.max_points, GL_DEPTH_COMPONENT32F)

        if create_fbos:
            self.spot_fbos = []
            for i in range(self.spot_depth_t.length):
                self.spot_fbos.append(RenderTarget([], ArrayLayerTarget(self.spot_depth_t, i)))
            
            self.sun_fbos = []
            for i in range(self.sun_depth_t.length):
                self.sun_fbos.append(RenderTarget([], ArrayLayerTarget(self.sun_depth_t, i)))
                    
            self.point_fbos = []
            for i in range(self.point_depth_t.length*6):
                self.point_fbos.append(RenderTarget([], ArrayLayerTarget(self.point_depth_t, i)))
        
    def clear(self, spot_count, sun_count, point_count):
        for i in range(spot_count):
            self.spot_fbos[i].clear(depth=1)
        for i in range(sun_count):
            self.sun_fbos[i].clear(depth=1)
        for i in range(point_count*6):
            self.point_fbos[i].clear(depth=1)
    
    def shader_callback(self, shader):
        shader.textures['SHADOWMAPS_DEPTH_SPOT'] = self.spot_depth_t
        shader.textures['SHADOWMAPS_DEPTH_SUN'] = self.sun_depth_t
        shader.textures['SHADOWMAPS_DEPTH_POINT'] = self.point_depth_t


class LightsBuffer(object):
    
    def __init__(self):
        self.data = C_LightsBuffer()
        self.UBO = UBO()
        self.spots = None
        self.suns = None
        self.points = None
    
    def load(self, scene, cascades_count, cascades_distribution_scalar, cascades_max_distance=1.0):
        #TODO: Automatic distribution exponent basedd on FOV

        spot_count=0
        sun_count=0
        point_count=0

        from collections import OrderedDict

        self.spots = OrderedDict()
        self.suns = OrderedDict()
        self.points = OrderedDict()

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

                projection_matrix = make_projection_matrix(light.spot_angle,1,0.01,light.radius)
                spot_matrix = projection_matrix * pyrr.Matrix44(light.matrix)
                
                self.data.spot_matrices[spot_count] = flatten_matrix(spot_matrix)

                self.spots[light] = [(light.matrix, flatten_matrix(projection_matrix))]

                spot_count+=1
            
            if light.type == LIGHT_SUN:
                self.data.lights[i].type_index = sun_count

                sun_matrix = pyrr.Matrix44(light.matrix)
                projection_matrix = pyrr.Matrix44(scene.camera.projection_matrix)
                view_matrix = projection_matrix * pyrr.Matrix44(scene.camera.camera_matrix)

                cascades_matrices = get_sun_cascades(sun_matrix, projection_matrix, view_matrix, cascades_count, cascades_distribution_scalar, cascades_max_distance)
                
                self.suns[light] = []
                for i, cascade in enumerate(cascades_matrices):
                    cascade = flatten_matrix(cascade)
                    self.data.sun_matrices[sun_count * cascades_count + i] = cascade
                    
                    self.suns[light].append((cascade, flatten_matrix(pyrr.Matrix44.identity())))

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

                self.points[light] = []
                for i in range(6):
                    self.points[light].append((flatten_matrix(matrices[i]), flatten_matrix(projection_matrix)))
                
                point_count+=1
            
        self.data.lights_count = len(scene.lights)
        self.data.cascades_count = cascades_count
        
        self.UBO.load_data(self.data)
    
    def bind(self, location):
        self.UBO.bind(location)


def flatten_matrix(matrix):
    return (ctypes.c_float * 16)(*[e for v in matrix for e in v])


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


def get_sun_cascades(sun_from_world_matrix, projection_matrix, view_from_world_matrix, cascades_count, cascades_distribution_scalar, cascades_max_distance):
    cascades = []
    splits = []

    n,f = 0,0    
    if projection_matrix[3][3] == 1.0:
        # ortho
        n = cascades_max_distance / 2
        f = -cascades_max_distance / 2
    else:
        # perspective
        clip_start = projection_matrix.inverse * pyrr.Vector4([0,0,-1,1])
        clip_start /= clip_start.w
        n = clip_start.z
        f = -cascades_max_distance

    def lerp(a,b,f):
        f = max(0,min(f,1))
        return a * (1.0 - f) + b * f

    for i in range(cascades_count+1):
        split_log = n * pow(f/n, i/cascades_count)
        split_uniform = n + (f-n) * (i/cascades_count)
        split = lerp(split_uniform, split_log, cascades_distribution_scalar)

        projected = projection_matrix * pyrr.Vector4([0,0,split,1])
        projected = (projected / projected.w) * (1.0 if projected.w >= 0 else -1.0)
        splits.append(projected.z)
        
    for i in range(1, len(splits)):
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

