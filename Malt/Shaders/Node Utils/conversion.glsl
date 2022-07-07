#ifndef CONVERSION_GLSL
#define CONVERSION_GLSL

/*  META GLOBAL
    @meta: internal = true;
*/

//float
float float_from_int(int i) { return float(i); }
float float_from_uint(uint u) { return float(u); }
float float_from_bool(bool b) { return float(b); }

//int
int int_from_float(float f) { return int(f); }
int int_from_uint(uint u) { return int(u); }
int int_from_bool(bool b) { return int(b); }

//uint
uint uint_from_float(float f) { return uint(f); }
uint uint_from_int(int i) { return uint(i); }
uint uint_from_bool(bool b) { return uint(b); }

//bool
bool bool_from_float(float f) { return bool(f); }
bool bool_from_int(int i) { return bool(i); }
bool bool_from_uint(uint u) { return bool(u); }

//vec2
vec2 vec2_from_float(float f) { return vec2(f); }
vec2 vec2_from_int(int i) { return vec2(i); }
vec2 vec2_from_uint(uint u) { return vec2(u); }
vec2 vec2_from_bool(bool b) { return vec2(b); }
vec2 vec2_from_vec3(vec3 v) { return vec2(v.xy); }
vec2 vec2_from_vec4(vec4 v) { return vec2(v.xy); }
vec2 vec2_from_ivec2(ivec2 v) { return vec2(v); }
vec2 vec2_from_ivec3(ivec3 v) { return vec2(v.xy); }
vec2 vec2_from_ivec4(ivec4 v) { return vec2(v.xy); }
vec2 vec2_from_uvec2(uvec2 v) { return vec2(v); }
vec2 vec2_from_uvec3(uvec3 v) { return vec2(v.xy); }
vec2 vec2_from_uvec4(uvec4 v) { return vec2(v.xy); }
vec2 vec2_from_bvec2(bvec2 v) { return vec2(v); }
vec2 vec2_from_bvec3(bvec3 v) { return vec2(v.xy); }
vec2 vec2_from_bvec4(bvec4 v) { return vec2(v.xy); }

//vec3
vec3 vec3_from_float(float f) { return vec3(f); }
vec3 vec3_from_int(int i) { return vec3(i); }
vec3 vec3_from_uint(uint u) { return vec3(u); }
vec3 vec3_from_bool(bool b) { return vec3(b); }
vec3 vec3_from_vec2(vec2 v) { return vec3(v, 0); }
vec3 vec3_from_vec4(vec4 v) { return vec3(v.xyz); }
vec3 vec3_from_ivec2(ivec2 v) { return vec3(v, 0); }
vec3 vec3_from_ivec3(ivec3 v) { return vec3(v); }
vec3 vec3_from_ivec4(ivec4 v) { return vec3(v.xyz); }
vec3 vec3_from_uvec2(uvec2 v) { return vec3(v, 0); }
vec3 vec3_from_uvec3(uvec3 v) { return vec3(v); }
vec3 vec3_from_uvec4(uvec4 v) { return vec3(v.xyz); }
vec3 vec3_from_bvec2(bvec2 v) { return vec3(v, 0); }
vec3 vec3_from_bvec3(bvec3 v) { return vec3(v); }
vec3 vec3_from_bvec4(bvec4 v) { return vec3(v.xyz); }

//vec4
vec4 vec4_from_float(float f) { return vec4(f, f, f, 1); }
vec4 vec4_from_int(int i) { return vec4(i, i, i, 1); }
vec4 vec4_from_uint(uint u) { return vec4(u, u, u, 1); }
vec4 vec4_from_bool(bool b) { return vec4(b, b, b, 1); }
vec4 vec4_from_vec2(vec2 v) { return vec4(v, 0, 1); }
vec4 vec4_from_vec3(vec3 v) { return vec4(v, 1); }
vec4 vec4_from_ivec2(ivec2 v) { return vec4(v, 0, 1); }
vec4 vec4_from_ivec3(ivec3 v) { return vec4(v, 1); }
vec4 vec4_from_ivec4(ivec4 v) { return vec4(v); }
vec4 vec4_from_uvec2(uvec2 v) { return vec4(v, 0, 1); }
vec4 vec4_from_uvec3(uvec3 v) { return vec4(v, 1); }
vec4 vec4_from_uvec4(uvec4 v) { return vec4(v); }
vec4 vec4_from_bvec2(bvec2 v) { return vec4(v, 0, 1); }
vec4 vec4_from_bvec3(bvec3 v) { return vec4(v, 1); }
vec4 vec4_from_bvec4(bvec4 v) { return vec4(v); }

//ivec2
ivec2 ivec2_from_float(float f) { return ivec2(f); }
ivec2 ivec2_from_int(int i) { return ivec2(i); }
ivec2 ivec2_from_uint(uint u) { return ivec2(u); }
ivec2 ivec2_from_bool(bool b) { return ivec2(b); }
ivec2 ivec2_from_vec2(vec2 v) { return ivec2(v); }
ivec2 ivec2_from_vec3(vec3 v) { return ivec2(v.xy); }
ivec2 ivec2_from_vec4(vec4 v) { return ivec2(v.xy); }
ivec2 ivec2_from_ivec3(ivec3 v) { return ivec2(v.xy); }
ivec2 ivec2_from_ivec4(ivec4 v) { return ivec2(v.xy); }
ivec2 ivec2_from_uvec2(uvec2 v) { return ivec2(v); }
ivec2 ivec2_from_uvec3(uvec3 v) { return ivec2(v.xy); }
ivec2 ivec2_from_uvec4(uvec4 v) { return ivec2(v.xy); }
ivec2 ivec2_from_bvec2(bvec2 v) { return ivec2(v); }
ivec2 ivec2_from_bvec3(bvec3 v) { return ivec2(v.xy); }
ivec2 ivec2_from_bvec4(bvec4 v) { return ivec2(v.xy); }

//ivec3
ivec3 ivec3_from_float(float f) { return ivec3(f); }
ivec3 ivec3_from_int(int i) { return ivec3(i); }
ivec3 ivec3_from_uint(uint u) { return ivec3(u); }
ivec3 ivec3_from_bool(bool b) { return ivec3(b); }
ivec3 ivec3_from_vec2(vec2 v) { return ivec3(v, 0); }
ivec3 ivec3_from_vec3(vec3 v) { return ivec3(v); }
ivec3 ivec3_from_vec4(vec4 v) { return ivec3(v.xyz); }
ivec3 ivec3_from_ivec2(ivec2 v) { return ivec3(v, 0); }
ivec3 ivec3_from_ivec4(ivec4 v) { return ivec3(v.xyz); }
ivec3 ivec3_from_uvec2(uvec2 v) { return ivec3(v, 0); }
ivec3 ivec3_from_uvec3(uvec3 v) { return ivec3(v); }
ivec3 ivec3_from_uvec4(uvec4 v) { return ivec3(v.xyz); }
ivec3 ivec3_from_bvec2(bvec2 v) { return ivec3(v, 0); }
ivec3 ivec3_from_bvec3(bvec3 v) { return ivec3(v); }
ivec3 ivec3_from_bvec4(bvec4 v) { return ivec3(v.xyz); }

//ivec4
ivec4 ivec4_from_float(float f) { return ivec4(f, f, f, 1); }
ivec4 ivec4_from_int(int i) { return ivec4(i, i, i, 1); }
ivec4 ivec4_from_uint(uint u) { return ivec4(u, u, u, 1); }
ivec4 ivec4_from_bool(bool b) { return ivec4(b, b, b, 1); }
ivec4 ivec4_from_vec2(vec2 v) { return ivec4(v, 0, 1); }
ivec4 ivec4_from_vec3(vec3 v) { return ivec4(v, 1); }
ivec4 ivec4_from_vec4(vec4 v) { return ivec4(v); }
ivec4 ivec4_from_ivec2(ivec2 v) { return ivec4(v, 0, 1); }
ivec4 ivec4_from_ivec3(ivec3 v) { return ivec4(v, 1); }
ivec4 ivec4_from_uvec2(uvec2 v) { return ivec4(v, 0, 1); }
ivec4 ivec4_from_uvec3(uvec3 v) { return ivec4(v, 1); }
ivec4 ivec4_from_uvec4(uvec4 v) { return ivec4(v); }
ivec4 ivec4_from_bvec2(bvec2 v) { return ivec4(v, 0, 1); }
ivec4 ivec4_from_bvec3(bvec3 v) { return ivec4(v, 1); }
ivec4 ivec4_from_bvec4(bvec4 v) { return ivec4(v); }

//uvec2
uvec2 uvec2_from_float(float f) { return uvec2(f); }
uvec2 uvec2_from_int(int i) { return uvec2(i); }
uvec2 uvec2_from_uint(uint u) { return uvec2(u); }
uvec2 uvec2_from_bool(bool b) { return uvec2(b); }
uvec2 uvec2_from_vec2(vec2 v) { return uvec2(v); }
uvec2 uvec2_from_vec3(vec3 v) { return uvec2(v.xy); }
uvec2 uvec2_from_vec4(vec4 v) { return uvec2(v.xy); }
uvec2 uvec2_from_ivec2(ivec2 v) { return uvec2(v); }
uvec2 uvec2_from_ivec3(ivec3 v) { return uvec2(v.xy); }
uvec2 uvec2_from_ivec4(ivec4 v) { return uvec2(v.xy); }
uvec2 uvec2_from_uvec3(uvec3 v) { return uvec2(v.xy); }
uvec2 uvec2_from_uvec4(uvec4 v) { return uvec2(v.xy); }
uvec2 uvec2_from_bvec2(bvec2 v) { return uvec2(v); }
uvec2 uvec2_from_bvec3(bvec3 v) { return uvec2(v.xy); }
uvec2 uvec2_from_bvec4(bvec4 v) { return uvec2(v.xy); }

//uvec3
uvec3 uvec3_from_float(float f) { return uvec3(f); }
uvec3 uvec3_from_int(int i) { return uvec3(i); }
uvec3 uvec3_from_uint(uint u) { return uvec3(u); }
uvec3 uvec3_from_bool(bool b) { return uvec3(b); }
uvec3 uvec3_from_vec2(vec2 v) { return uvec3(v, 0); }
uvec3 uvec3_from_vec3(vec3 v) { return uvec3(v); }
uvec3 uvec3_from_vec4(vec4 v) { return uvec3(v.xyz); }
uvec3 uvec3_from_ivec2(ivec2 v) { return uvec3(v, 0); }
uvec3 uvec3_from_ivec3(ivec3 v) { return uvec3(v); }
uvec3 uvec3_from_ivec4(ivec4 v) { return uvec3(v.xyz); }
uvec3 uvec3_from_uvec2(uvec2 v) { return uvec3(v, 0); }
uvec3 uvec3_from_uvec4(uvec4 v) { return uvec3(v.xyz); }
uvec3 uvec3_from_bvec2(bvec2 v) { return uvec3(v, 0); }
uvec3 uvec3_from_bvec3(bvec3 v) { return uvec3(v); }
uvec3 uvec3_from_bvec4(bvec4 v) { return uvec3(v.xyz); }

//uvec4
uvec4 uvec4_from_float(float f) { return uvec4(f, f, f, 1); }
uvec4 uvec4_from_int(int i) { return uvec4(i, i, i, 1); }
uvec4 uvec4_from_uint(uint u) { return uvec4(u, u, u, 1); }
uvec4 uvec4_from_bool(bool b) { return uvec4(b, b, b, 1); }
uvec4 uvec4_from_vec2(vec2 v) { return uvec4(v, 0, 1); }
uvec4 uvec4_from_vec3(vec3 v) { return uvec4(v, 1); }
uvec4 uvec4_from_vec4(vec4 v) { return uvec4(v); }
uvec4 uvec4_from_ivec2(ivec2 v) { return uvec4(v, 0, 1); }
uvec4 uvec4_from_ivec3(ivec3 v) { return uvec4(v, 1); }
uvec4 uvec4_from_ivec4(ivec4 v) { return uvec4(v); }
uvec4 uvec4_from_uvec2(uvec2 v) { return uvec4(v, 0, 1); }
uvec4 uvec4_from_uvec3(uvec3 v) { return uvec4(v, 1); }
uvec4 uvec4_from_bvec2(bvec2 v) { return uvec4(v, 0, 1); }
uvec4 uvec4_from_bvec3(bvec3 v) { return uvec4(v, 1); }
uvec4 uvec4_from_bvec4(bvec4 v) { return uvec4(v); }

//bvec2
bvec2 bvec2_from_float(float f) { return bvec2(f); }
bvec2 bvec2_from_int(int i) { return bvec2(i); }
bvec2 bvec2_from_uint(uint u) { return bvec2(u); }
bvec2 bvec2_from_bool(bool b) { return bvec2(b); }
bvec2 bvec2_from_vec2(vec2 v) { return bvec2(v); }
bvec2 bvec2_from_vec3(vec3 v) { return bvec2(v.xy); }
bvec2 bvec2_from_vec4(vec4 v) { return bvec2(v.xy); }
bvec2 bvec2_from_ivec2(ivec2 v) { return bvec2(v); }
bvec2 bvec2_from_ivec3(ivec3 v) { return bvec2(v.xy); }
bvec2 bvec2_from_ivec4(ivec4 v) { return bvec2(v.xy); }
bvec2 bvec2_from_uvec2(uvec2 v) { return bvec2(v); }
bvec2 bvec2_from_uvec3(uvec3 v) { return bvec2(v.xy); }
bvec2 bvec2_from_uvec4(uvec4 v) { return bvec2(v.xy); }
bvec2 bvec2_from_bvec3(bvec3 v) { return bvec2(v.xy); }
bvec2 bvec2_from_bvec4(bvec4 v) { return bvec2(v.xy); }

//bvec3
bvec3 bvec3_from_float(float f) { return bvec3(f); }
bvec3 bvec3_from_int(int i) { return bvec3(i); }
bvec3 bvec3_from_uint(uint u) { return bvec3(u); }
bvec3 bvec3_from_bool(bool b) { return bvec3(b); }
bvec3 bvec3_from_vec2(vec2 v) { return bvec3(v, 0); }
bvec3 bvec3_from_vec3(vec3 v) { return bvec3(v); }
bvec3 bvec3_from_vec4(vec4 v) { return bvec3(v.xyz); }
bvec3 bvec3_from_ivec2(ivec2 v) { return bvec3(v, 0); }
bvec3 bvec3_from_ivec3(ivec3 v) { return bvec3(v); }
bvec3 bvec3_from_ivec4(ivec4 v) { return bvec3(v.xyz); }
bvec3 bvec3_from_uvec2(uvec2 v) { return bvec3(v, 0); }
bvec3 bvec3_from_uvec3(uvec3 v) { return bvec3(v); }
bvec3 bvec3_from_uvec4(uvec4 v) { return bvec3(v.xyz); }
bvec3 bvec3_from_bvec2(bvec2 v) { return bvec3(v, 0); }
bvec3 bvec3_from_bvec4(bvec4 v) { return bvec3(v.xyz); }

//bvec4
bvec4 bvec4_from_float(float f) { return bvec4(f); }
bvec4 bvec4_from_int(int i) { return bvec4(i); }
bvec4 bvec4_from_uint(uint u) { return bvec4(u); }
bvec4 bvec4_from_bool(bool b) { return bvec4(b); }
bvec4 bvec4_from_vec2(vec2 v) { return bvec4(v, 0, 0); }
bvec4 bvec4_from_vec3(vec3 v) { return bvec4(v, 0); }
bvec4 bvec4_from_vec4(vec4 v) { return bvec4(v); }
bvec4 bvec4_from_ivec2(ivec2 v) { return bvec4(v, 0, 0); }
bvec4 bvec4_from_ivec3(ivec3 v) { return bvec4(v, 0); }
bvec4 bvec4_from_ivec4(ivec4 v) { return bvec4(v); }
bvec4 bvec4_from_uvec2(uvec2 v) { return bvec4(v, 0, 0); }
bvec4 bvec4_from_uvec3(uvec3 v) { return bvec4(v, 0); }
bvec4 bvec4_from_uvec4(uvec4 v) { return bvec4(v); }
bvec4 bvec4_from_bvec2(bvec2 v) { return bvec4(v, 0, 0); }
bvec4 bvec4_from_bvec3(bvec3 v) { return bvec4(v, 0); }

#endif //CONVERSION_GLSL
