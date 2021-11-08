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

uniform sampler2D IN_0;
uniform sampler2D IN_1;
uniform sampler2D IN_2;
uniform sampler2D IN_3;

uniform sampler2D IN_DEPTH;

layout (location = 0) out vec4 OUT_0;
layout (location = 1) out vec4 OUT_1;
layout (location = 2) out vec4 OUT_2;
layout (location = 3) out vec4 OUT_3;

void main()
{
    ivec2 uv = ivec2(gl_FragCoord.xy);
    
    OUT_0 = texelFetch(IN_0, uv, 0);
    OUT_1 = texelFetch(IN_1, uv, 0);
    OUT_2 = texelFetch(IN_2, uv, 0);
    OUT_3 = texelFetch(IN_3, uv, 0);

    gl_FragDepth = texelFetch(IN_DEPTH, uv, 0).x;
}

#endif //PIXEL_SHADER
