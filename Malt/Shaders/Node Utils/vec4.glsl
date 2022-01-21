#ifndef VEC4_GLSL
#define VEC4_GLSL

/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_add(vec4 a, vec4 b){ return a+b; }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_subtract(vec4 a, vec4 b){ return a-b; }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_multiply(vec4 a, vec4 b){ return a*b; }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_divide(vec4 a, vec4 b){ return a/b; }
/*META @v: subtype=Vector;*/
vec4 vec4_scale(vec4 v, float s){ return v*s; }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_modulo(vec4 a, vec4 b){ return mod(a,b); }
/*META @v: subtype=Vector; @e: subtype=Vector;*/
vec4 vec4_pow(vec4 v, vec4 e){ return pow(v, e); }
/*META @v: subtype=Vector;*/
vec4 vec4_sqrt(vec4 v){ return sqrt(v); }

/*META @v: subtype=Vector;*/
vec4 vec4_round(vec4 v){ return round(v); }
/*META @v: subtype=Vector;*/
vec4 vec4_fract(vec4 v){ return fract(v); }
/*META @v: subtype=Vector;*/
vec4 vec4_floor(vec4 v){ return floor(v); }
/*META @v: subtype=Vector;*/
vec4 vec4_ceil(vec4 v){ return ceil(v); }

/*META @v: subtype=Vector; @min: subtype=Vector; @max: subtype=Vector;*/
vec4 vec4_clamp(vec4 v, vec4 min, vec4 max){ return clamp(v, min, max); }

/*META @v: subtype=Vector;*/
vec4 vec4_sign(vec4 v){ return sign(v); }
/*META @v: subtype=Vector;*/
vec4 vec4_abs(vec4 v){ return abs(v); }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_min(vec4 a, vec4 b){ return min(a,b); }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_max(vec4 a, vec4 b){ return max(a,b); }

/*META @a: subtype=Vector; @b: subtype=Vector; @factor: subtype=Vector;*/
vec4 vec4_mix(vec4 a, vec4 b, vec4 factor){ return mix(a,b,factor); }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_mix_float(vec4 a, vec4 b, float factor){ return mix(a,b,factor); }

/*META @v: subtype=Vector;*/
float vec4_length(vec4 v){ return length(v); }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
float vec4_distance(vec4 a, vec4 b){ return distance(a,b); }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
float vec4_dot_product(vec4 a, vec4 b){ return dot(a,b); }

/*META @a: subtype=Vector; @b: subtype=Vector;*/
bool vec4_equal(vec4 a, vec4 b){ return a == b; }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
bool vec4_not_equal(vec4 a, vec4 b){ return a != b; }

/*META @if_true: subtype=Vector; @if_false: subtype=Vector;*/
vec4 vec4_if_else(bool condition, vec4 if_true, vec4 if_false){ return condition ? if_true : if_false; }

vec4 vec4_join(float r, float g, float b, float a) { return vec4(r,g,b,a);}
/*META @v: subtype=Vector;*/
void vec4_split(vec4 v, out float r, out float g, out float b, out float a){ r=v.r; g=v.g; b=v.b; a=v.a; }

#endif //VEC4_GLSL
