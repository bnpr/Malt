#ifndef VEC3_GLSL
#define VEC3_GLSL

vec3 vec3_property(vec3 v) { return v; }

vec3 vec3_add(vec3 a, vec3 b){ return a+b; }
vec3 vec3_subtract(vec3 a, vec3 b){ return a-b; }
vec3 vec3_multiply(vec3 a, vec3 b){ return a*b; }
vec3 vec3_divide(vec3 a, vec3 b){ return a/b; }
vec3 vec3_scale(vec3 v, float s){ return v*s; }
vec3 vec3_modulo(vec3 a, vec3 b){ return mod(a,b); }
vec3 vec3_pow(vec3 v, vec3 e){ return pow(v, e); }
vec3 vec3_sqrt(vec3 v){ return sqrt(v); }

vec3 vec3_round(vec3 v){ return round(v); }
vec3 vec3_fract(vec3 v){ return fract(v); }
vec3 vec3_floor(vec3 v){ return floor(v); }
vec3 vec3_ceil(vec3 v){ return ceil(v); }

vec3 vec3_clamp(vec3 v, vec3 min, vec3 max){ return clamp(v, min, max); }

vec3 vec3_sign(vec3 v){ return sign(v); }
vec3 vec3_abs(vec3 v){ return abs(v); }
vec3 vec3_min(vec3 a, vec3 b){ return min(a,b); }
vec3 vec3_max(vec3 a, vec3 b){ return max(a,b); }

vec3 vec3_mix(vec3 a, vec3 b, vec3 factor){ return mix(a,b,factor); }
vec3 vec3_mix_float(vec3 a, vec3 b, float factor){ return mix(a,b,factor); }

float vec3_length(vec3 v){ return length(v); }
float vec3_distance(vec3 a, vec3 b){ return distance(a,b); }
float vec3_dot_product(vec3 a, vec3 b){ return dot(a,b); }
vec3 vec3_cross_product(vec3 a, vec3 b){ return cross(a,b); }

bool vec3_equal(vec3 a, vec3 b){ return a == b; }
bool vec3_not_equal(vec3 a, vec3 b){ return a != b; }

vec3 vec3_if_else(bool condition, vec3 a, vec3 b){ return condition ? a : b; }

vec3 vec3_join(float x, float y, float z) { return vec3(x,y,z);}
void vec3_split(vec3 v, out float x, out float y, out float z){ x=v.x; y=v.y; z=v.z; }
vec3 vec3_from_float(float f) { return vec3(f); }
vec3 vec3_from_vec2(vec2 v) { return vec3(v, 0); }
vec3 vec3_from_vec2(vec2 v, float z) { return vec3(v, z); }
vec3 vec3_from_vec4(vec4 v) { return v.xyz; }

#endif //VEC3_GLSL
