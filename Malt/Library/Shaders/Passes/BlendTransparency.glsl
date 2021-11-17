//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#include "Common.glsl"
#include "Common/Color.glsl"

#ifdef VERTEX_SHADER
void main()
{
    POSITION = in_position;
    UV[0] = in_position.xy * 0.5 + 0.5;

    gl_Position = vec4(POSITION, 1);
}
#endif

#ifdef PIXEL_SHADER

uniform sampler2D IN_BACK;
uniform sampler2D IN_FRONT;

layout (location = 0) out vec4 OUT_RESULT;

void main()
{
    vec4 back = texelFetch(IN_BACK, ivec2(gl_FragCoord.xy), 0);
    vec4 front = texelFetch(IN_FRONT, ivec2(gl_FragCoord.xy), 0);

    OUT_RESULT = alpha_blend(back, front);
}

#endif //PIXEL_SHADER
