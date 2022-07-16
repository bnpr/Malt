#ifndef VEC3_GLSL
#define VEC3_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Vector 3D;
*/

/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_add(vec3 a, vec3 b){ return a+b; }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_subtract(vec3 a, vec3 b){ return a-b; }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_multiply(vec3 a, vec3 b){ return a*b; }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_divide(vec3 a, vec3 b){ return a/b; }
/*META @v: subtype=Vector;*/
vec3 vec3_scale(vec3 v, float s){ return v*s; }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_modulo(vec3 a, vec3 b){ return mod(a,b); }
/*META @v: subtype=Vector; @e: subtype=Vector;*/
vec3 vec3_pow(vec3 v, vec3 e){ return pow(v, e); }
/*META @v: subtype=Vector;*/
vec3 vec3_sqrt(vec3 v){ return sqrt(v); }

/*META @v: subtype=Vector;*/
vec3 vec3_round(vec3 v){ return round(v); }
/*META @v: subtype=Vector;*/
vec3 vec3_fract(vec3 v){ return fract(v); }
/*META @v: subtype=Vector;*/
vec3 vec3_floor(vec3 v){ return floor(v); }
/*META @v: subtype=Vector;*/
vec3 vec3_ceil(vec3 v){ return ceil(v); }

/*META @v: subtype=Vector; @min: subtype=Vector; @max: subtype=Vector;*/
vec3 vec3_clamp(vec3 v, vec3 min, vec3 max){ return clamp(v, min, max); }

/*META @v: subtype=Vector;*/
vec3 vec3_sign(vec3 v){ return sign(v); }
/*META @v: subtype=Vector;*/
vec3 vec3_abs(vec3 v){ return abs(v); }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_min(vec3 a, vec3 b){ return min(a,b); }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_max(vec3 a, vec3 b){ return max(a,b); }

/*META @a: subtype=Vector; @b: subtype=Vector; @factor: subtype=Vector;*/
vec3 vec3_mix(vec3 a, vec3 b, vec3 factor){ return mix(a,b,factor); }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_mix_float(vec3 a, vec3 b, float factor){ return mix(a,b,factor); }

/*META @v: subtype=Vector;*/
vec3 vec3_normalize(vec3 v){ return normalize(v); }

/*META @v: subtype=Vector;*/
float vec3_length(vec3 v){ return length(v); }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
float vec3_distance(vec3 a, vec3 b){ return distance(a,b); }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
float vec3_dot_product(vec3 a, vec3 b){ return dot(a,b); }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_cross_product(vec3 a, vec3 b){ return cross(a,b); }

/*META @a: subtype=Vector; @b: subtype=Vector;*/
bool vec3_equal(vec3 a, vec3 b){ return a == b; }
/*META @a: subtype=Vector; @b: subtype=Vector;*/
bool vec3_not_equal(vec3 a, vec3 b){ return a != b; }

/*META @if_true: subtype=Vector; @if_false: subtype=Vector;*/
vec3 vec3_if_else(bool condition, vec3 if_true, vec3 if_false){ return condition ? if_true : if_false; }

vec3 vec3_join(float x, float y, float z) { return vec3(x,y,z);}
/*META @v: subtype=Vector;*/
void vec3_split(vec3 v, out float x, out float y, out float z){ x=v.x; y=v.y; z=v.z; }

#endif //VEC3_GLSL
