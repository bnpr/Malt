//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    POSITION = in_position;
    UV[0] = in_position.xy * 0.5 + 0.5;
    
    VERTEX_SETUP_OUTPUT();

    gl_Position = vec4(POSITION, 1);
}
#endif

#ifdef PIXEL_SHADER

#include "Filters/Line.glsl"

layout (location = 0) out vec4 OUT_RESULT;

uniform sampler2D color_texture;

uniform sampler2D depth_texture;
uniform int depth_channel;

uniform usampler2D id_texture;
uniform int id_channel;

uniform sampler2D line_color_texture;

uniform sampler2D line_width_texture;
uniform int line_width_channel;

uniform float aa_offset = 0.0;

uniform int brute_force_range = 10;

void main()
{
    PIXEL_SETUP_INPUT();

    vec2 uv = screen_uv();
    vec4 line_color = line_expand(
        uv, brute_force_range, aa_offset,
        line_color_texture, line_width_texture, line_width_channel,
        depth_texture, depth_channel, id_texture, id_channel
    ).color;

    vec4 color = texture(color_texture, uv);
    
    OUT_RESULT = alpha_blend(color, line_color);
}

#endif //PIXEL_SHADER
