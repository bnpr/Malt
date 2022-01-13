#include "Common.glsl"
#include "Common/Color.glsl"

#ifdef VERTEX_SHADER
void main()
{
    gl_Position = vec4(in_position, 1);
}
#endif

#ifdef PIXEL_SHADER

uniform sampler2D IN_BACK[8];
uniform sampler2D IN_FRONT[8];

layout (location = 0) out vec4 OUT_RESULT_0;
layout (location = 1) out vec4 OUT_RESULT_1;
layout (location = 2) out vec4 OUT_RESULT_2;
layout (location = 3) out vec4 OUT_RESULT_3;
layout (location = 4) out vec4 OUT_RESULT_4;
layout (location = 5) out vec4 OUT_RESULT_5;
layout (location = 6) out vec4 OUT_RESULT_6;
layout (location = 7) out vec4 OUT_RESULT_7;

void main()
{
    PIXEL_SETUP_INPUT();

    ivec2 uv = ivec2(gl_FragCoord.xy);

    OUT_RESULT_0 = alpha_blend(texelFetch(IN_BACK[0], uv, 0), texelFetch(IN_FRONT[0], uv, 0));
    OUT_RESULT_1 = alpha_blend(texelFetch(IN_BACK[1], uv, 0), texelFetch(IN_FRONT[1], uv, 0));
    OUT_RESULT_2 = alpha_blend(texelFetch(IN_BACK[2], uv, 0), texelFetch(IN_FRONT[2], uv, 0));
    OUT_RESULT_3 = alpha_blend(texelFetch(IN_BACK[3], uv, 0), texelFetch(IN_FRONT[3], uv, 0));
    OUT_RESULT_4 = alpha_blend(texelFetch(IN_BACK[4], uv, 0), texelFetch(IN_FRONT[4], uv, 0));
    OUT_RESULT_5 = alpha_blend(texelFetch(IN_BACK[5], uv, 0), texelFetch(IN_FRONT[5], uv, 0));
    OUT_RESULT_6 = alpha_blend(texelFetch(IN_BACK[6], uv, 0), texelFetch(IN_FRONT[6], uv, 0));
    OUT_RESULT_7 = alpha_blend(texelFetch(IN_BACK[7], uv, 0), texelFetch(IN_FRONT[7], uv, 0));
}

#endif //PIXEL_SHADER
