#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    DEFAULT_SCREEN_VERTEX_SHADER();
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
    PIXEL_SETUP_INPUT();

    uvec4 packed_pixel = texture(IN_PACKED, UV[0]);    
    OUT_A = unpackUnorm4x8(packed_pixel.r);
    OUT_B = unpackUnorm4x8(packed_pixel.g);
    OUT_C = unpackUnorm4x8(packed_pixel.b);
    OUT_D = unpackUnorm4x8(packed_pixel.a);
}

#endif //PIXEL_SHADER
