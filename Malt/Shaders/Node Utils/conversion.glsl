#ifndef CONVERSION_GLSL
#define CONVERSION_GLSL

/* META @meta: internal=true; */
float float_from_int(int i) { return float(i); }

/* META @meta: internal=true; */
int int_from_float(float f) { return int(f); }
/* META @meta: internal=true; */
int int_from_uint(uint u) { return int(u); }

/* META @meta: internal=true; */
uint uint_from_float(float f) { return uint(f); }
/* META @meta: internal=true; */
uint uint_from_int(int i) { return uint(i); }

/* META @meta: internal=true; */
vec2 vec2_from_float(float f) { return vec2(f); }
/* META @meta: internal=true; */
vec2 vec2_from_vec3(vec3 v) { return v.xy; }
/* META @meta: internal=true; */
vec2 vec2_from_vec4(vec4 v) { return v.xy; }

/* META @meta: internal=true; */
vec3 vec3_from_float(float f) { return vec3(f); }
/* META @meta: internal=true; */
vec3 vec3_from_vec2(vec2 v) { return vec3(v, 0); }
/* META @meta: internal=true; */
vec3 vec3_from_vec4(vec4 v) { return v.xyz; }

/* META @meta: internal=true; */
vec4 vec4_from_float(float f) { return vec4(f, f, f, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_vec2(vec2 v) { return vec4(v, 0, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_vec3(vec3 v) { return vec4(v, 1); }

/* META @meta: internal=true; */
bvec2 bvec2_from_vec2(vec2 v) { return bvec2(v); }
/* META @meta: internal=true; */
ivec2 ivec2_from_vec2(vec2 v) { return ivec2(v); }
/* META @meta: internal=true; */
uvec2 uvec2_from_vec2(vec2 v) { return uvec2(v); }
/* META @meta: internal=true; */
vec2 vec2_from_bvec2(bvec2 v) { return vec2(v); }
/* META @meta: internal=true; */
vec2 vec2_from_ivec2(ivec2 v) { return vec2(v); }
/* META @meta: internal=true; */
vec2 vec2_from_uvec2(uvec2 v) { return vec2(v); }

/* META @meta: internal=true; */
bvec3 bvec3_from_vec3(vec3 v) { return bvec3(v); }
/* META @meta: internal=true; */
ivec3 ivec3_from_vec3(vec3 v) { return ivec3(v); }
/* META @meta: internal=true; */
uvec3 uvec3_from_vec3(vec3 v) { return uvec3(v); }
/* META @meta: internal=true; */
vec3 vec3_from_bvec3(bvec3 v) { return vec3(v); }
/* META @meta: internal=true; */
vec3 vec3_from_ivec3(ivec3 v) { return vec3(v); }
/* META @meta: internal=true; */
vec3 vec3_from_uvec3(uvec3 v) { return vec3(v); }

/* META @meta: internal=true; */
bvec4 bvec4_from_vec4(vec4 v) { return bvec4(v); }
/* META @meta: internal=true; */
ivec4 ivec4_from_vec4(vec4 v) { return ivec4(v); }
/* META @meta: internal=true; */
uvec4 uvec4_from_vec4(vec4 v) { return uvec4(v); }
/* META @meta: internal=true; */
vec4 vec4_from_bvec4(bvec4 v) { return vec4(v); }
/* META @meta: internal=true; */
vec4 vec4_from_ivec4(ivec4 v) { return vec4(v); }
/* META @meta: internal=true; */
vec4 vec4_from_uvec4(uvec4 v) { return vec4(v); }

#endif //CONVERSION_GLSL
