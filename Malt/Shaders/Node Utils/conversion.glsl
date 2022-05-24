#ifndef CONVERSION_GLSL
#define CONVERSION_GLSL

//float
/* META @meta: internal=true; */
float float_from_int(int i) { return float(i); }
/* META @meta: internal=true; */
float float_from_uint(uint u) { return float(u); }
/* META @meta: internal=true; */
float float_from_bool(bool b) { return float(b); }

//int
/* META @meta: internal=true; */
int int_from_float(float f) { return int(f); }
/* META @meta: internal=true; */
int int_from_uint(uint u) { return int(u); }
/* META @meta: internal=true; */
int int_from_bool(bool b) { return int(b); }

//uint
/* META @meta: internal=true; */
uint uint_from_float(float f) { return uint(f); }
/* META @meta: internal=true; */
uint uint_from_int(int i) { return uint(i); }
/* META @meta: internal=true; */
uint uint_from_bool(bool b) { return uint(b); }

//bool
/* META @meta: internal=true; */
bool bool_from_float(float f) { return bool(f); }
/* META @meta: internal=true; */
bool bool_from_int(int i) { return bool(i); }
/* META @meta: internal=true; */
bool bool_from_uint(uint u) { return bool(u); }

//vec2
/* META @meta: internal=true; */
vec2 vec2_from_float(float f) { return vec2(f); }
/* META @meta: internal=true; */
vec2 vec2_from_int(int i) { return vec2(i); }
/* META @meta: internal=true; */
vec2 vec2_from_uint(uint u) { return vec2(u); }
/* META @meta: internal=true; */
vec2 vec2_from_bool(bool b) { return vec2(b); }
/* META @meta: internal=true; */
vec2 vec2_from_vec3(vec3 v) { return vec2(v.xy); }
/* META @meta: internal=true; */
vec2 vec2_from_vec4(vec4 v) { return vec2(v.xy); }
/* META @meta: internal=true; */
vec2 vec2_from_ivec2(ivec2 v) { return vec2(v); }
/* META @meta: internal=true; */
vec2 vec2_from_ivec3(ivec3 v) { return vec2(v.xy); }
/* META @meta: internal=true; */
vec2 vec2_from_ivec4(ivec4 v) { return vec2(v.xy); }
/* META @meta: internal=true; */
vec2 vec2_from_uvec2(uvec2 v) { return vec2(v); }
/* META @meta: internal=true; */
vec2 vec2_from_uvec3(uvec3 v) { return vec2(v.xy); }
/* META @meta: internal=true; */
vec2 vec2_from_uvec4(uvec4 v) { return vec2(v.xy); }
/* META @meta: internal=true; */
vec2 vec2_from_bvec2(bvec2 v) { return vec2(v); }
/* META @meta: internal=true; */
vec2 vec2_from_bvec3(bvec3 v) { return vec2(v.xy); }
/* META @meta: internal=true; */
vec2 vec2_from_bvec4(bvec4 v) { return vec2(v.xy); }

//vec3
/* META @meta: internal=true; */
vec3 vec3_from_float(float f) { return vec3(f); }
/* META @meta: internal=true; */
vec3 vec3_from_int(int i) { return vec3(i); }
/* META @meta: internal=true; */
vec3 vec3_from_uint(uint u) { return vec3(u); }
/* META @meta: internal=true; */
vec3 vec3_from_bool(bool b) { return vec3(b); }
/* META @meta: internal=true; */
vec3 vec3_from_vec2(vec2 v) { return vec3(v, 0); }
/* META @meta: internal=true; */
vec3 vec3_from_vec4(vec4 v) { return vec3(v.xyz); }
/* META @meta: internal=true; */
vec3 vec3_from_ivec2(ivec2 v) { return vec3(v, 0); }
/* META @meta: internal=true; */
vec3 vec3_from_ivec3(ivec3 v) { return vec3(v); }
/* META @meta: internal=true; */
vec3 vec3_from_ivec4(ivec4 v) { return vec3(v.xyz); }
/* META @meta: internal=true; */
vec3 vec3_from_uvec2(uvec2 v) { return vec3(v, 0); }
/* META @meta: internal=true; */
vec3 vec3_from_uvec3(uvec3 v) { return vec3(v); }
/* META @meta: internal=true; */
vec3 vec3_from_uvec4(uvec4 v) { return vec3(v.xyz); }
/* META @meta: internal=true; */
vec3 vec3_from_bvec2(bvec2 v) { return vec3(v, 0); }
/* META @meta: internal=true; */
vec3 vec3_from_bvec3(bvec3 v) { return vec3(v); }
/* META @meta: internal=true; */
vec3 vec3_from_bvec4(bvec4 v) { return vec3(v.xyz); }

//vec4
/* META @meta: internal=true; */
vec4 vec4_from_float(float f) { return vec4(f, f, f, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_int(int i) { return vec4(i, i, i, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_uint(uint u) { return vec4(u, u, u, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_bool(bool b) { return vec4(b, b, b, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_vec2(vec2 v) { return vec4(v, 0, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_vec3(vec3 v) { return vec4(v, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_ivec2(ivec2 v) { return vec4(v, 0, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_ivec3(ivec3 v) { return vec4(v, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_ivec4(ivec4 v) { return vec4(v); }
/* META @meta: internal=true; */
vec4 vec4_from_uvec2(uvec2 v) { return vec4(v, 0, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_uvec3(uvec3 v) { return vec4(v, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_uvec4(uvec4 v) { return vec4(v); }
/* META @meta: internal=true; */
vec4 vec4_from_bvec2(bvec2 v) { return vec4(v, 0, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_bvec3(bvec3 v) { return vec4(v, 1); }
/* META @meta: internal=true; */
vec4 vec4_from_bvec4(bvec4 v) { return vec4(v); }

//ivec2
/* META @meta: internal=true; */
ivec2 ivec2_from_float(float f) { return ivec2(f); }
/* META @meta: internal=true; */
ivec2 ivec2_from_int(int i) { return ivec2(i); }
/* META @meta: internal=true; */
ivec2 ivec2_from_uint(uint u) { return ivec2(u); }
/* META @meta: internal=true; */
ivec2 ivec2_from_bool(bool b) { return ivec2(b); }
/* META @meta: internal=true; */
ivec2 ivec2_from_vec2(vec2 v) { return ivec2(v); }
/* META @meta: internal=true; */
ivec2 ivec2_from_vec3(vec3 v) { return ivec2(v.xy); }
/* META @meta: internal=true; */
ivec2 ivec2_from_vec4(vec4 v) { return ivec2(v.xy); }
/* META @meta: internal=true; */
ivec2 ivec2_from_ivec3(ivec3 v) { return ivec2(v.xy); }
/* META @meta: internal=true; */
ivec2 ivec2_from_ivec4(ivec4 v) { return ivec2(v.xy); }
/* META @meta: internal=true; */
ivec2 ivec2_from_uvec2(uvec2 v) { return ivec2(v); }
/* META @meta: internal=true; */
ivec2 ivec2_from_uvec3(uvec3 v) { return ivec2(v.xy); }
/* META @meta: internal=true; */
ivec2 ivec2_from_uvec4(uvec4 v) { return ivec2(v.xy); }
/* META @meta: internal=true; */
ivec2 ivec2_from_bvec2(bvec2 v) { return ivec2(v); }
/* META @meta: internal=true; */
ivec2 ivec2_from_bvec3(bvec3 v) { return ivec2(v.xy); }
/* META @meta: internal=true; */
ivec2 ivec2_from_bvec4(bvec4 v) { return ivec2(v.xy); }

//ivec3
/* META @meta: internal=true; */
ivec3 ivec3_from_float(float f) { return ivec3(f); }
/* META @meta: internal=true; */
ivec3 ivec3_from_int(int i) { return ivec3(i); }
/* META @meta: internal=true; */
ivec3 ivec3_from_uint(uint u) { return ivec3(u); }
/* META @meta: internal=true; */
ivec3 ivec3_from_bool(bool b) { return ivec3(b); }
/* META @meta: internal=true; */
ivec3 ivec3_from_vec2(vec2 v) { return ivec3(v, 0); }
/* META @meta: internal=true; */
ivec3 ivec3_from_vec3(vec3 v) { return ivec3(v); }
/* META @meta: internal=true; */
ivec3 ivec3_from_vec4(vec4 v) { return ivec3(v.xyz); }
/* META @meta: internal=true; */
ivec3 ivec3_from_ivec2(ivec2 v) { return ivec3(v, 0); }
/* META @meta: internal=true; */
ivec3 ivec3_from_ivec4(ivec4 v) { return ivec3(v.xyz); }
/* META @meta: internal=true; */
ivec3 ivec3_from_uvec2(uvec2 v) { return ivec3(v, 0); }
/* META @meta: internal=true; */
ivec3 ivec3_from_uvec3(uvec3 v) { return ivec3(v); }
/* META @meta: internal=true; */
ivec3 ivec3_from_uvec4(uvec4 v) { return ivec3(v.xyz); }
/* META @meta: internal=true; */
ivec3 ivec3_from_bvec2(bvec2 v) { return ivec3(v, 0); }
/* META @meta: internal=true; */
ivec3 ivec3_from_bvec3(bvec3 v) { return ivec3(v); }
/* META @meta: internal=true; */
ivec3 ivec3_from_bvec4(bvec4 v) { return ivec3(v.xyz); }

//ivec4
/* META @meta: internal=true; */
ivec4 ivec4_from_float(float f) { return ivec4(f, f, f, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_int(int i) { return ivec4(i, i, i, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_uint(uint u) { return ivec4(u, u, u, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_bool(bool b) { return ivec4(b, b, b, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_vec2(vec2 v) { return ivec4(v, 0, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_vec3(vec3 v) { return ivec4(v, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_vec4(vec4 v) { return ivec4(v); }
/* META @meta: internal=true; */
ivec4 ivec4_from_ivec2(ivec2 v) { return ivec4(v, 0, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_ivec3(ivec3 v) { return ivec4(v, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_uvec2(uvec2 v) { return ivec4(v, 0, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_uvec3(uvec3 v) { return ivec4(v, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_uvec4(uvec4 v) { return ivec4(v); }
/* META @meta: internal=true; */
ivec4 ivec4_from_bvec2(bvec2 v) { return ivec4(v, 0, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_bvec3(bvec3 v) { return ivec4(v, 1); }
/* META @meta: internal=true; */
ivec4 ivec4_from_bvec4(bvec4 v) { return ivec4(v); }

//uvec2
/* META @meta: internal=true; */
uvec2 uvec2_from_float(float f) { return uvec2(f); }
/* META @meta: internal=true; */
uvec2 uvec2_from_int(int i) { return uvec2(i); }
/* META @meta: internal=true; */
uvec2 uvec2_from_uint(uint u) { return uvec2(u); }
/* META @meta: internal=true; */
uvec2 uvec2_from_bool(bool b) { return uvec2(b); }
/* META @meta: internal=true; */
uvec2 uvec2_from_vec2(vec2 v) { return uvec2(v); }
/* META @meta: internal=true; */
uvec2 uvec2_from_vec3(vec3 v) { return uvec2(v.xy); }
/* META @meta: internal=true; */
uvec2 uvec2_from_vec4(vec4 v) { return uvec2(v.xy); }
/* META @meta: internal=true; */
uvec2 uvec2_from_ivec2(ivec2 v) { return uvec2(v); }
/* META @meta: internal=true; */
uvec2 uvec2_from_ivec3(ivec3 v) { return uvec2(v.xy); }
/* META @meta: internal=true; */
uvec2 uvec2_from_ivec4(ivec4 v) { return uvec2(v.xy); }
/* META @meta: internal=true; */
uvec2 uvec2_from_uvec3(uvec3 v) { return uvec2(v.xy); }
/* META @meta: internal=true; */
uvec2 uvec2_from_uvec4(uvec4 v) { return uvec2(v.xy); }
/* META @meta: internal=true; */
uvec2 uvec2_from_bvec2(bvec2 v) { return uvec2(v); }
/* META @meta: internal=true; */
uvec2 uvec2_from_bvec3(bvec3 v) { return uvec2(v.xy); }
/* META @meta: internal=true; */
uvec2 uvec2_from_bvec4(bvec4 v) { return uvec2(v.xy); }

//uvec3
/* META @meta: internal=true; */
uvec3 uvec3_from_float(float f) { return uvec3(f); }
/* META @meta: internal=true; */
uvec3 uvec3_from_int(int i) { return uvec3(i); }
/* META @meta: internal=true; */
uvec3 uvec3_from_uint(uint u) { return uvec3(u); }
/* META @meta: internal=true; */
uvec3 uvec3_from_bool(bool b) { return uvec3(b); }
/* META @meta: internal=true; */
uvec3 uvec3_from_vec2(vec2 v) { return uvec3(v, 0); }
/* META @meta: internal=true; */
uvec3 uvec3_from_vec3(vec3 v) { return uvec3(v); }
/* META @meta: internal=true; */
uvec3 uvec3_from_vec4(vec4 v) { return uvec3(v.xyz); }
/* META @meta: internal=true; */
uvec3 uvec3_from_ivec2(ivec2 v) { return uvec3(v, 0); }
/* META @meta: internal=true; */
uvec3 uvec3_from_ivec3(ivec3 v) { return uvec3(v); }
/* META @meta: internal=true; */
uvec3 uvec3_from_ivec4(ivec4 v) { return uvec3(v.xyz); }
/* META @meta: internal=true; */
uvec3 uvec3_from_uvec2(uvec2 v) { return uvec3(v, 0); }
/* META @meta: internal=true; */
uvec3 uvec3_from_uvec4(uvec4 v) { return uvec3(v.xyz); }
/* META @meta: internal=true; */
uvec3 uvec3_from_bvec2(bvec2 v) { return uvec3(v, 0); }
/* META @meta: internal=true; */
uvec3 uvec3_from_bvec3(bvec3 v) { return uvec3(v); }
/* META @meta: internal=true; */
uvec3 uvec3_from_bvec4(bvec4 v) { return uvec3(v.xyz); }

//uvec4
/* META @meta: internal=true; */
uvec4 uvec4_from_float(float f) { return uvec4(f, f, f, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_int(int i) { return uvec4(i, i, i, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_uint(uint u) { return uvec4(u, u, u, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_bool(bool b) { return uvec4(b, b, b, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_vec2(vec2 v) { return uvec4(v, 0, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_vec3(vec3 v) { return uvec4(v, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_vec4(vec4 v) { return uvec4(v); }
/* META @meta: internal=true; */
uvec4 uvec4_from_ivec2(ivec2 v) { return uvec4(v, 0, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_ivec3(ivec3 v) { return uvec4(v, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_ivec4(ivec4 v) { return uvec4(v); }
/* META @meta: internal=true; */
uvec4 uvec4_from_uvec2(uvec2 v) { return uvec4(v, 0, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_uvec3(uvec3 v) { return uvec4(v, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_bvec2(bvec2 v) { return uvec4(v, 0, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_bvec3(bvec3 v) { return uvec4(v, 1); }
/* META @meta: internal=true; */
uvec4 uvec4_from_bvec4(bvec4 v) { return uvec4(v); }

//bvec2
/* META @meta: internal=true; */
bvec2 bvec2_from_float(float f) { return bvec2(f); }
/* META @meta: internal=true; */
bvec2 bvec2_from_int(int i) { return bvec2(i); }
/* META @meta: internal=true; */
bvec2 bvec2_from_uint(uint u) { return bvec2(u); }
/* META @meta: internal=true; */
bvec2 bvec2_from_bool(bool b) { return bvec2(b); }
/* META @meta: internal=true; */
bvec2 bvec2_from_vec2(vec2 v) { return bvec2(v); }
/* META @meta: internal=true; */
bvec2 bvec2_from_vec3(vec3 v) { return bvec2(v.xy); }
/* META @meta: internal=true; */
bvec2 bvec2_from_vec4(vec4 v) { return bvec2(v.xy); }
/* META @meta: internal=true; */
bvec2 bvec2_from_ivec2(ivec2 v) { return bvec2(v); }
/* META @meta: internal=true; */
bvec2 bvec2_from_ivec3(ivec3 v) { return bvec2(v.xy); }
/* META @meta: internal=true; */
bvec2 bvec2_from_ivec4(ivec4 v) { return bvec2(v.xy); }
/* META @meta: internal=true; */
bvec2 bvec2_from_uvec2(uvec2 v) { return bvec2(v); }
/* META @meta: internal=true; */
bvec2 bvec2_from_uvec3(uvec3 v) { return bvec2(v.xy); }
/* META @meta: internal=true; */
bvec2 bvec2_from_uvec4(uvec4 v) { return bvec2(v.xy); }
/* META @meta: internal=true; */
bvec2 bvec2_from_bvec3(bvec3 v) { return bvec2(v.xy); }
/* META @meta: internal=true; */
bvec2 bvec2_from_bvec4(bvec4 v) { return bvec2(v.xy); }

//bvec3
/* META @meta: internal=true; */
bvec3 bvec3_from_float(float f) { return bvec3(f); }
/* META @meta: internal=true; */
bvec3 bvec3_from_int(int i) { return bvec3(i); }
/* META @meta: internal=true; */
bvec3 bvec3_from_uint(uint u) { return bvec3(u); }
/* META @meta: internal=true; */
bvec3 bvec3_from_bool(bool b) { return bvec3(b); }
/* META @meta: internal=true; */
bvec3 bvec3_from_vec2(vec2 v) { return bvec3(v, 0); }
/* META @meta: internal=true; */
bvec3 bvec3_from_vec3(vec3 v) { return bvec3(v); }
/* META @meta: internal=true; */
bvec3 bvec3_from_vec4(vec4 v) { return bvec3(v.xyz); }
/* META @meta: internal=true; */
bvec3 bvec3_from_ivec2(ivec2 v) { return bvec3(v, 0); }
/* META @meta: internal=true; */
bvec3 bvec3_from_ivec3(ivec3 v) { return bvec3(v); }
/* META @meta: internal=true; */
bvec3 bvec3_from_ivec4(ivec4 v) { return bvec3(v.xyz); }
/* META @meta: internal=true; */
bvec3 bvec3_from_uvec2(uvec2 v) { return bvec3(v, 0); }
/* META @meta: internal=true; */
bvec3 bvec3_from_uvec3(uvec3 v) { return bvec3(v); }
/* META @meta: internal=true; */
bvec3 bvec3_from_uvec4(uvec4 v) { return bvec3(v.xyz); }
/* META @meta: internal=true; */
bvec3 bvec3_from_bvec2(bvec2 v) { return bvec3(v, 0); }
/* META @meta: internal=true; */
bvec3 bvec3_from_bvec4(bvec4 v) { return bvec3(v.xyz); }

//bvec4
/* META @meta: internal=true; */
bvec4 bvec4_from_float(float f) { return bvec4(f); }
/* META @meta: internal=true; */
bvec4 bvec4_from_int(int i) { return bvec4(i); }
/* META @meta: internal=true; */
bvec4 bvec4_from_uint(uint u) { return bvec4(u); }
/* META @meta: internal=true; */
bvec4 bvec4_from_bool(bool b) { return bvec4(b); }
/* META @meta: internal=true; */
bvec4 bvec4_from_vec2(vec2 v) { return bvec4(v, 0, 0); }
/* META @meta: internal=true; */
bvec4 bvec4_from_vec3(vec3 v) { return bvec4(v, 0); }
/* META @meta: internal=true; */
bvec4 bvec4_from_vec4(vec4 v) { return bvec4(v); }
/* META @meta: internal=true; */
bvec4 bvec4_from_ivec2(ivec2 v) { return bvec4(v, 0, 0); }
/* META @meta: internal=true; */
bvec4 bvec4_from_ivec3(ivec3 v) { return bvec4(v, 0); }
/* META @meta: internal=true; */
bvec4 bvec4_from_ivec4(ivec4 v) { return bvec4(v); }
/* META @meta: internal=true; */
bvec4 bvec4_from_uvec2(uvec2 v) { return bvec4(v, 0, 0); }
/* META @meta: internal=true; */
bvec4 bvec4_from_uvec3(uvec3 v) { return bvec4(v, 0); }
/* META @meta: internal=true; */
bvec4 bvec4_from_uvec4(uvec4 v) { return bvec4(v); }
/* META @meta: internal=true; */
bvec4 bvec4_from_bvec2(bvec2 v) { return bvec4(v, 0, 0); }
/* META @meta: internal=true; */
bvec4 bvec4_from_bvec3(bvec3 v) { return bvec4(v, 0); }

#endif //CONVERSION_GLSL
