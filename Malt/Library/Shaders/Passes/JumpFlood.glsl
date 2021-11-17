//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

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

#include "Filters/JumpFlood.glsl"

uniform sampler2D input_texture;
uniform float width;

layout (location = 0) out vec4 OUT_RESULT;

void main()
{
    vec2 uv = screen_uv();
    OUT_RESULT = jump_flood(input_texture, uv, width, true);
}

#endif //PIXEL_SHADER
