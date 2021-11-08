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

uniform usampler2D IN_PACKED;

layout (location = 0) out vec4 OUT_A;
layout (location = 1) out vec4 OUT_B;
layout (location = 2) out vec4 OUT_C;
layout (location = 3) out vec4 OUT_D;

void main()
{
    uvec4 packed_pixel = texture(IN_PACKED, UV[0]);    
    OUT_A = unpackUnorm4x8(packed_pixel.r);
    OUT_B = unpackUnorm4x8(packed_pixel.g);
    OUT_C = unpackUnorm4x8(packed_pixel.b);
    OUT_D = unpackUnorm4x8(packed_pixel.a);
}

#endif //PIXEL_SHADER
