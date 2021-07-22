//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

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

#include "Filters/Line.glsl"

uniform sampler2D color_texture;
uniform sampler2D depth_texture;
uniform sampler2D id_texture;
uniform sampler2D line_color_texture;
uniform sampler2D line_data_texture;
uniform float aa_offset = 0.0;

layout (location = 0) out vec4 OUT_RESULT;

uniform int brute_force_range = 10;

void main()
{
    vec2 uv = screen_uv();
    vec4 line_color = line_expand(
        uv, brute_force_range, aa_offset,
        line_color_texture, line_data_texture, 2,
        depth_texture, 0, id_texture, 0
    ).color;

    vec4 color = texture(color_texture, uv);
    
    OUT_RESULT = alpha_blend(color, line_color);
}

#endif //PIXEL_SHADER
