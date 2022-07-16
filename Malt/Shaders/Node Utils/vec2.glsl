#ifndef VEC2_GLSL
#define VEC2_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Vector 2D;
*/

vec2 vec2_add(vec2 a, vec2 b){ return a+b; }
vec2 vec2_subtract(vec2 a, vec2 b){ return a-b; }
vec2 vec2_multiply(vec2 a, vec2 b){ return a*b; }
vec2 vec2_divide(vec2 a, vec2 b){ return a/b; }
vec2 vec2_scale(vec2 v, float s){ return v*s; }
vec2 vec2_modulo(vec2 a, vec2 b){ return mod(a,b); }
vec2 vec2_pow(vec2 v, vec2 e){ return pow(v, e); }
vec2 vec2_sqrt(vec2 v){ return sqrt(v); }

vec2 vec2_round(vec2 v){ return round(v); }
vec2 vec2_fract(vec2 v){ return fract(v); }
vec2 vec2_floor(vec2 v){ return floor(v); }
vec2 vec2_ceil(vec2 v){ return ceil(v); }

vec2 vec2_clamp(vec2 v, vec2 min, vec2 max){ return clamp(v, min, max); }

vec2 vec2_sign(vec2 v){ return sign(v); }
vec2 vec2_abs(vec2 v){ return abs(v); }
vec2 vec2_min(vec2 a, vec2 b){ return min(a,b); }
vec2 vec2_max(vec2 a, vec2 b){ return max(a,b); }

vec2 vec2_mix(vec2 a, vec2 b, vec2 factor){ return mix(a,b,factor); }
vec2 vec2_mix_float(vec2 a, vec2 b, float factor){ return mix(a,b,factor); }

vec2 vec2_normalize(vec2 v){ return normalize(v); }

float vec2_length(vec2 v){ return length(v); }
float vec2_distance(vec2 a, vec2 b){ return distance(a,b); }
float vec2_dot_product(vec2 a, vec2 b){ return dot(a,b); }

bool vec2_equal(vec2 a, vec2 b){ return a == b; }
bool vec2_not_equal(vec2 a, vec2 b){ return a != b; }

vec2 vec2_if_else(bool condition, vec2 if_true, vec2 if_false){ return condition ? if_true : if_false; }

vec2 vec2_join(float x, float y) { return vec2(x,y);}
void vec2_split(vec2 v, out float x, out float y){ x=v.x; y=v.y; }

#endif //VEC2_GLSL
