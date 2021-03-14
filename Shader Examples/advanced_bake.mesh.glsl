//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#if defined(VERTEX_SHADER) && (defined(PRE_PASS) || defined(MAIN_PASS))
#define CUSTOM_MAIN
#endif

#include "Pipelines/NPR_Pipeline.glsl"

uniform float bake = 1.0;

#if defined(VERTEX_SHADER) && (defined(PRE_PASS) || defined(MAIN_PASS))
void main()
{
    DEFAULT_VERTEX_SHADER();
    VERTEX_SETUP_OUTPUT();
    vec4 bake_position = vec4(UV[0] * 2 - 1, -0.99, 1);
    gl_Position = mix(gl_Position, bake_position, saturate(bake));
}
#endif

#include "basic.mesh.glsl"
