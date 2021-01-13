//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef COMMON_GLSL
#define COMMON_GLSL

#ifdef VERTEX_SHADER

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec4 in_tangent0;
layout (location = 3) in vec4 in_tangent1;
layout (location = 4) in vec4 in_tangent2;
layout (location = 5) in vec4 in_tangent3;
layout (location = 6) in vec2 in_uv0;
layout (location = 7) in vec2 in_uv1;
layout (location = 8) in vec2 in_uv2;
layout (location = 9) in vec2 in_uv3;
layout (location = 10) in vec4 in_color0;
layout (location = 11) in vec4 in_color1;
layout (location = 12) in vec4 in_color2;
layout (location = 13) in vec4 in_color3;

out vec3 POSITION;
out vec3 NORMAL;
out vec3 TANGENT[4];
out vec3 BITANGENT[4];
out vec2 UV[4];
out vec4 COLOR[4];

out mat4 MODEL;
out float ID;

#endif //VERTEX_SHADER

#ifdef PIXEL_SHADER

in vec3 POSITION;
in vec3 NORMAL;
in vec3 TANGENT[4];
in vec3 BITANGENT[4];
in vec2 UV[4];
in vec4 COLOR[4];

in mat4 MODEL;
in float ID;

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
    uniform float BATCH_ID[MAX_BATCH_SIZE];
};

uniform bool MIRROR_SCALE = false;

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

    if(in_tangent0.xyz == vec3(0)) //No precomputed tangents
    {
        vec3 axis = vec3(0,0,1);
        axis = abs(dot(axis, in_normal)) < 0.99 ? axis : vec3(1,0,0);
        vec3 tangent = normalize(cross(axis, in_normal));
        tangent = transform_normal(MODEL, tangent);
        
        for(int i = 0; i < 4; i++) TANGENT[i] = tangent;
    }
    else
    {
        TANGENT[0]= transform_normal(MODEL, in_tangent0.xyz);
        TANGENT[1]= transform_normal(MODEL, in_tangent1.xyz);
        TANGENT[2]= transform_normal(MODEL, in_tangent2.xyz);
        TANGENT[3]= transform_normal(MODEL, in_tangent3.xyz);
    }

    BITANGENT[0]= normalize(cross(NORMAL, TANGENT[0]) * in_tangent0.w);
    BITANGENT[1]= normalize(cross(NORMAL, TANGENT[1]) * in_tangent1.w);
    BITANGENT[2]= normalize(cross(NORMAL, TANGENT[2]) * in_tangent2.w);
    BITANGENT[3]= normalize(cross(NORMAL, TANGENT[3]) * in_tangent3.w);

    if(MIRROR_SCALE)
    {
        for(int i = 0; i < 4; i++)
        {
            BITANGENT[i] *= -1;
        }
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

#define VERTEX_DISPLACEMENT(displacement_function, tangent_offset)\
{\
    vec3 displaced_position = displacement_function(POSITION);\
    for(int i = 0; i < TANGENT.length(); i++)\
    {\
        vec3 displaced_tangent = displacement_function(POSITION + TANGENT[i] * (tangent_offset));\
        vec3 displaced_bitangent = displacement_function(POSITION + BITANGENT[i] * (tangent_offset));\
        TANGENT[i] = normalize(displaced_tangent - displaced_position);\
        BITANGENT[i] = normalize(displaced_bitangent - displaced_position);\
    }\
    POSITION = displaced_position;\
    NORMAL = normalize(cross(TANGENT[0], BITANGENT[0]));\
}\

#endif //VERTEX_SHADER

#endif //COMMON_GLSL

