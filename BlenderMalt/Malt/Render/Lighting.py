# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import ctypes

GLSL = """
#define MAX_LIGHTS 64
    
struct SunLight
{
    vec3 color;
    vec3 direction;
};

struct PointLight
{
    vec3 color;
    vec3 position;
    float radius;
};

struct SpotLight
{
    vec3 color;
    vec3 position;
    vec3 direction;
    float angle;
    float angle_blend;
    float radius;
};

struct SceneLights
{
    SunLight sun_lights [MAX_LIGHTS];
    PointLight point_lights [MAX_LIGHTS];
    SpotLight spot_lights [MAX_LIGHTS];
    int sun_lights_count;
    int point_lights_count;
    int spot_lights_count;
};

layout(std140) uniform scene_lights_block
{
    SceneLights scene_lights;
};
"""

class C_SunLight(ctypes.Structure):
    _fields_ = [
        ('color', ctypes.c_float*3),
        ('__padding', ctypes.c_int32),
        ('direction', ctypes.c_float*3),
        ('__padding', ctypes.c_int32),
    ]

class C_PointLight(ctypes.Structure):
    
    _fields_ = [
        ('color', ctypes.c_float*3),
        ('__padding', ctypes.c_int32),
        ('position', ctypes.c_float*3),
        ('radius', ctypes.c_float),
    ]

class C_SpotLight(ctypes.Structure):
    
    _fields_ = [
        ('color', ctypes.c_float*3),
        ('__padding', ctypes.c_int32),
        ('position', ctypes.c_float*3),
        ('__padding', ctypes.c_int32),
        ('direction', ctypes.c_float*3),
        ('angle', ctypes.c_float),
        ('angle_blend', ctypes.c_float),
        ('radius', ctypes.c_float),
        ('__padding', ctypes.c_int32),
        ('__padding', ctypes.c_int32),
    ]

class LightsBuffer(ctypes.Structure):
    
    _fields_ = [
        ('sun_lights', C_SunLight*64),
        ('point_lights', C_PointLight*64),
        ('spot_lights', C_SpotLight*64),
        ('sun_lights_count', ctypes.c_int),
        ('point_lights_count', ctypes.c_int),
        ('spot_lights_count', ctypes.c_int),
        ('__padding', ctypes.c_int32),
    ]

