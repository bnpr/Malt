//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    gl_Position = vec4(in_position, 1);
}
#endif

#ifdef PIXEL_SHADER

uniform sampler2D IN[8];

uniform sampler2D IN_DEPTH;

layout (location = 0) out vec4 OUT_0;
layout (location = 1) out vec4 OUT_1;
layout (location = 2) out vec4 OUT_2;
layout (location = 3) out vec4 OUT_3;
layout (location = 4) out vec4 OUT_4;
layout (location = 5) out vec4 OUT_5;
layout (location = 6) out vec4 OUT_6;
layout (location = 7) out vec4 OUT_7;

void main()
{
    PIXEL_SETUP_INPUT();

    ivec2 uv = ivec2(gl_FragCoord.xy);
    
    OUT_0 = texelFetch(IN[0], uv, 0);
    OUT_1 = texelFetch(IN[1], uv, 0);
    OUT_2 = texelFetch(IN[2], uv, 0);
    OUT_3 = texelFetch(IN[3], uv, 0);
    OUT_4 = texelFetch(IN[4], uv, 0);
    OUT_5 = texelFetch(IN[5], uv, 0);
    OUT_6 = texelFetch(IN[6], uv, 0);
    OUT_7 = texelFetch(IN[7], uv, 0);

    gl_FragDepth = texelFetch(IN_DEPTH, uv, 0).x;
}

#endif //PIXEL_SHADER
