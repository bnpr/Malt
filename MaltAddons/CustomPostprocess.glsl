//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#version 410 core
#extension GL_ARB_shading_language_include : enable

#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    POSITION = in_position;
    UV[0] = in_position.xy * 0.5 + 0.5;

    gl_Position = vec4(POSITION, 1);
}
#endif

#ifdef PIXEL_SHADER

#include "Common/Color.glsl"

uniform sampler2D IN_RENDER;
uniform vec3 multiply_color = vec3(1.0);

layout (location = 0) out vec4 OUT_RESULT;

void main()
{
    vec4 color = texture(IN_RENDER, UV[0]);
    vec3 hsv = rgb_to_hsv(color.rgb);
    hsv.y = 0;
    color.rgb = hsv_to_rgb(hsv);
    OUT_RESULT = color * vec4(multiply_color, 1.0);
}

#endif //PIXEL_SHADER
