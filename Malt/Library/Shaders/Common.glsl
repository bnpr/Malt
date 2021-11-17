//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#ifndef COMMON_GLSL
#define COMMON_GLSL

#include "Common/Meta.glsl"

#ifdef VERTEX_SHADER

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec4 in_tangent;
layout (location = 3) in vec2 in_uv0;
layout (location = 4) in vec2 in_uv1;
layout (location = 5) in vec2 in_uv2;
layout (location = 6) in vec2 in_uv3;
layout (location = 7) in vec4 in_color0;
layout (location = 8) in vec4 in_color1;
layout (location = 9) in vec4 in_color2;
layout (location = 10) in vec4 in_color3;

out vec3 POSITION;
out vec3 NORMAL;
out vec3 TANGENT;
out vec3 BITANGENT;
out vec2 UV[4];
out vec4 COLOR[4];

out mat4 MODEL;
flat out uint ID;

#endif //VERTEX_SHADER

#ifdef PIXEL_SHADER

in vec3 POSITION;
in vec3 NORMAL;
in vec3 TANGENT;
in vec3 BITANGENT;
in vec2 UV[4];
in vec4 COLOR[4];

in mat4 MODEL;
flat in uint ID;

#endif //PIXEL_SHADER

#ifndef MAX_BATCH_SIZE
    // Assume at least 64kb of UBO storage (d3d11 requirement) and max element size of mat4
    #define MAX_BATCH_SIZE 1000
#endif

layout(std140) uniform BATCH_MODELS
{
    uniform mat4 BATCH_MODEL[MAX_BATCH_SIZE];
};
uniform BATCH_IDS
{
    uniform uint BATCH_ID[MAX_BATCH_SIZE];
};

uniform bool MIRROR_SCALE = false;
uniform bool PRECOMPUTED_TANGENTS = false;

layout(std140) uniform COMMON_UNIFORMS
{
    uniform mat4 CAMERA;
    uniform mat4 PROJECTION;
    uniform ivec2 RESOLUTION;
    uniform vec2 SAMPLE_OFFSET;
    uniform int SAMPLE_COUNT;
    uniform int FRAME;
    uniform float TIME;
};

#include "Common/Color.glsl"
//#include "Lighting/Lighting.glsl"
#include "Common/Math.glsl"
#include "Common/Transform.glsl"

#ifdef VERTEX_SHADER

void VERTEX_SETUP_OUTPUT()
{
    gl_Position = PROJECTION * CAMERA * vec4(POSITION, 1);
    //Screen-Space offset for Temporal Super-Sampling 
    gl_Position.xy += (SAMPLE_OFFSET / vec2(RESOLUTION)) * gl_Position.w;
}

void DEFAULT_VERTEX_SHADER()
{
    MODEL = BATCH_MODEL[gl_InstanceID];
    ID = BATCH_ID[gl_InstanceID];

    POSITION = transform_point(MODEL, in_position);
    NORMAL = transform_normal(MODEL, in_normal);

    if(PRECOMPUTED_TANGENTS)
    {
        TANGENT = transform_normal(MODEL, in_tangent.xyz);
        float mirror_scale = MIRROR_SCALE ? -1 : 1;
        BITANGENT = normalize(cross(NORMAL, TANGENT) * in_tangent.w) * mirror_scale;
    }

    UV[0]=in_uv0;
    UV[1]=in_uv1;
    UV[2]=in_uv2;
    UV[3]=in_uv3;

    COLOR[0]=in_color0;
    COLOR[1]=in_color1;
    COLOR[2]=in_color2;
    COLOR[3]=in_color3;

    VERTEX_SETUP_OUTPUT();
}

#endif //VERTEX_SHADER

#endif //COMMON_GLSL

