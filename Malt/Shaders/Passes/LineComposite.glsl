#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    DEFAULT_SCREEN_VERTEX_SHADER();
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
uniform float line_width_scale = 1.0;

uniform int brute_force_range = 10;

void main()
{
    PIXEL_SETUP_INPUT();

    vec2 uv = screen_uv();
    vec4 line_color = line_expand(
        uv, brute_force_range,
        line_color_texture, line_width_texture, line_width_channel, line_width_scale,
        depth_texture, depth_channel, id_texture, id_channel
    ).color;

    vec4 color = texture(color_texture, uv);
    
    OUT_RESULT = alpha_blend(color, line_color);
}

#endif //PIXEL_SHADER
