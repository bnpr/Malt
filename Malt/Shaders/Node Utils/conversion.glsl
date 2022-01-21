#ifndef CONVERSION_GLSL
#define CONVERSION_GLSL

float float_from_int(int i) { return float(i); }

int int_from_float(float f) { return int(f); }
int int_from_uint(uint u) { return int(u); }

uint uint_from_float(float f) { return uint(f); }
uint uint_from_int(int i) { return uint(i); }

vec2 vec2_from_float(float f) { return vec2(f); }
vec2 vec2_from_vec3(vec3 v) { return v.xy; }
vec2 vec2_from_vec4(vec4 v) { return v.xy; }

vec3 vec3_from_float(float f) { return vec3(f); }
vec3 vec3_from_vec2(vec2 v) { return vec3(v, 0); }
vec3 vec3_from_vec4(vec4 v) { return v.xyz; }

vec4 vec4_from_float(float f) { return vec4(f); }
vec4 vec4_from_vec2(vec2 v) { return vec4(v, 0, 1); }
vec4 vec4_from_vec3(vec3 v) { return vec4(v, 1); }

bvec2 bvec2_from_vec2(vec2 v) { return bvec2(v); }
ivec2 ivec2_from_vec2(vec2 v) { return ivec2(v); }
uvec2 uvec2_from_vec2(vec2 v) { return uvec2(v); }
vec2 vec2_from_bvec2(bvec2 v) { return vec2(v); }
vec2 vec2_from_ivec2(ivec2 v) { return vec2(v); }
vec2 vec2_from_uvec2(uvec2 v) { return vec2(v); }

bvec3 bvec3_from_vec3(vec3 v) { return bvec3(v); }
ivec3 ivec3_from_vec3(vec3 v) { return ivec3(v); }
uvec3 uvec3_from_vec3(vec3 v) { return uvec3(v); }
vec3 vec3_from_bvec3(bvec3 v) { return vec3(v); }
vec3 vec3_from_ivec3(ivec3 v) { return vec3(v); }
vec3 vec3_from_uvec3(uvec3 v) { return vec3(v); }

bvec4 bvec4_from_vec4(vec4 v) { return bvec4(v); }
ivec4 ivec4_from_vec4(vec4 v) { return ivec4(v); }
uvec4 uvec4_from_vec4(vec4 v) { return uvec4(v); }
vec4 vec4_from_bvec4(bvec4 v) { return vec4(v); }
vec4 vec4_from_ivec4(ivec4 v) { return vec4(v); }
vec4 vec4_from_uvec4(uvec4 v) { return vec4(v); }

#endif //CONVERSION_GLSL
