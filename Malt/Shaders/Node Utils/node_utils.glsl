#include "bool.glsl"

#include "float.glsl"
#include "int.glsl"

#include "vec2.glsl"
#include "vec3.glsl"
#include "vec4.glsl"

vec4 texture_sample(sampler2D t, vec2 uv) { return texture(t, uv); }
vec4 gradient_sample(sampler1D t, float u) { return texture(t, u); }

