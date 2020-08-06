//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Common.glsl"

#ifdef VERTEX_SHADER
void DEFAULT_COMMON_VERTEX_SHADER()
{
    DEFAULT_VERTEX_SHADER();
}
#endif

#ifdef PIXEL_SHADER

uniform float ID;

#ifdef PRE_PASS
layout (location = 0) out vec4 OUT_NORMAL_DEPTH;
layout (location = 1) out float OUT_ID;

void DEFAULT_PRE_PASS_PIXEL_SHADER()
{
    OUT_NORMAL_DEPTH.rgb = normalize(NORMAL);
    OUT_NORMAL_DEPTH.a = gl_FragCoord.z;
    OUT_ID = ID;
}
#endif //PRE_PASS

#ifdef MAIN_PASS
uniform sampler2D IN_NORMAL_DEPTH;
uniform sampler2D IN_ID;

layout (location = 0) out vec4 OUT_COLOR;

void DEFAULT_MAIN_PASS_PIXEL_SHADER()
{
    OUT_COLOR = vec4(1.0,1.0,0.0,1.0);
}
#endif //MAIN_PASS

#endif //PIXEL_SHADER
