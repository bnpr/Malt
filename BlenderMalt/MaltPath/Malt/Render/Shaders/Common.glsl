//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef COMMON_GLSL
#define COMMON_GLSL

#ifdef VERTEX_SHADER

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_uv0;
layout (location = 3) in vec2 in_uv1;
layout (location = 4) in vec2 in_uv2;
layout (location = 5) in vec2 in_uv3;
layout (location = 6) in vec2 in_uv4;
layout (location = 7) in vec2 in_uv5;
layout (location = 8) in vec2 in_uv6;
layout (location = 9) in vec2 in_uv7;
layout (location = 10) in vec4 in_color0;
layout (location = 11) in vec4 in_color1;
layout (location = 12) in vec4 in_color2;
layout (location = 13) in vec4 in_color3;
layout (location = 14) in vec4 in_color4;
layout (location = 15) in vec4 in_color5;
layout (location = 16) in vec4 in_color6;
layout (location = 17) in vec4 in_color7;

out vec3 POSITION;
out vec3 NORMAL;
out vec2 UV[8];
out vec4 COLOR[8];

#endif //VERTEX_SHADER

#ifdef PIXEL_SHADER

in vec3 POSITION;
in vec3 NORMAL;
in vec2 UV[8];
in vec4 COLOR[8];

#endif //PIXEL_SHADER

uniform mat4 MODEL;

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

#include "Common/Transform.glsl"
#include "Common/Lighting.glsl"

layout(std140) uniform SCENE_LIGHTS
{
    SceneLights LIGHTS;
};

#ifdef VERTEX_SHADER

void VERTEX_SETUP_OUTPUT()
{
    gl_Position = PROJECTION * CAMERA * vec4(POSITION, 1);
    //Screen-Space offset for Temporal Super-Sampling 
    gl_Position.xy += (SAMPLE_OFFSET / vec2(RESOLUTION)) * gl_Position.w;
}

void DEFAULT_VERTEX_SHADER()
{
    POSITION = transform_point(MODEL, in_position);
    NORMAL = transform_normal(MODEL, in_normal);

    UV[0]=in_uv0;
    UV[1]=in_uv1;
    UV[2]=in_uv2;
    UV[3]=in_uv3;
    UV[4]=in_uv4;
    UV[5]=in_uv5;
    UV[6]=in_uv6;
    UV[7]=in_uv7;

    COLOR[0]=in_color0;
    COLOR[1]=in_color1;
    COLOR[2]=in_color2;
    COLOR[3]=in_color3;
    COLOR[4]=in_color3;
    COLOR[5]=in_color3;
    COLOR[6]=in_color3;
    COLOR[7]=in_color3;

    VERTEX_SETUP_OUTPUT();
}

#endif //VERTEX_SHADER

#endif //COMMON_GLSL

