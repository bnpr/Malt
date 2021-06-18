#ifndef VEC4_GLSL
#define VEC4_GLSL

vec4 vec4_property(vec4 v) { return v; }

vec4 vec4_add(vec4 a, vec4 b){ return a+b; }
vec4 vec4_subtract(vec4 a, vec4 b){ return a-b; }
vec4 vec4_multiply(vec4 a, vec4 b){ return a*b; }
vec4 vec4_divide(vec4 a, vec4 b){ return a/b; }
vec4 vec4_scale(vec4 v, float s){ return v*s; }
vec4 vec4_modulo(vec4 a, vec4 b){ return mod(a,b); }
vec4 vec4_pow(vec4 v, vec4 e){ return pow(v, e); }
vec4 vec4_sqrt(vec4 v){ return sqrt(v); }

vec4 vec4_round(vec4 v){ return round(v); }
vec4 vec4_fract(vec4 v){ return fract(v); }
vec4 vec4_floor(vec4 v){ return floor(v); }
vec4 vec4_ceil(vec4 v){ return ceil(v); }

vec4 vec4_clamp(vec4 v, vec4 min, vec4 max){ return clamp(v, min, max); }

vec4 vec4_sign(vec4 v){ return sign(v); }
vec4 vec4_abs(vec4 v){ return abs(v); }
vec4 vec4_min(vec4 a, vec4 b){ return min(a,b); }
vec4 vec4_max(vec4 a, vec4 b){ return max(a,b); }

vec4 vec4_mix(vec4 a, vec4 b, vec4 factor){ return mix(a,b,factor); }
vec4 vec4_mix_float(vec4 a, vec4 b, float factor){ return mix(a,b,factor); }

float vec4_length(vec4 v){ return length(v); }
float vec4_distance(vec4 a, vec4 b){ return distance(a,b); }
float vec4_dot_product(vec4 a, vec4 b){ return dot(a,b); }

bool vec4_equal(vec4 a, vec4 b){ return a == b; }
bool vec4_not_equal(vec4 a, vec4 b){ return a != b; }

vec4 vec4_if_else(bool condition, vec4 a, vec4 b){ return condition ? a : b; }

vec4 vec4_join(float r, float g, float b, float a) { return vec4(r,g,b,a);}
void vec4_split(vec4 v, out float r, out float g, out float b, out float a){ r=v.r; g=v.g; b=v.b; a=v.a; }
vec4 vec4_from_float(float f) { return vec4(f); }
vec4 vec4_from_vec2(vec2 v, float b, float a) { return vec4(v, b, a); }
vec4 vec4_from_vec3(vec3 v, float a) { return vec4(v, a); }

#endif //VEC4_GLSL
