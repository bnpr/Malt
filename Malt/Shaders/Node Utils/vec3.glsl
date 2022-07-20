#ifndef VEC3_GLSL
#define VEC3_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Vector 3D;
*/

/*META @meta: label=Add; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_add(vec3 a, vec3 b){ return a+b; }
/*META @meta: label=Subtract; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_subtract(vec3 a, vec3 b){ return a-b; }
/*META @meta: label=Multiply; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_multiply(vec3 a, vec3 b){ return a*b; }
/*META @meta: label=Divide; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_divide(vec3 a, vec3 b){ return a/b; }
/*META @meta: label=Scale; @v: subtype=Vector;*/
vec3 vec3_scale(vec3 v, float s){ return v*s; }
/*META @meta: label=Modulo; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_modulo(vec3 a, vec3 b){ return mod(a,b); }
/*META @meta: label=Power; @v: subtype=Vector; @e: subtype=Vector;*/
vec3 vec3_pow(vec3 v, vec3 e){ return pow(v, e); }
/*META @meta: label=Square Root; @v: subtype=Vector;*/
vec3 vec3_sqrt(vec3 v){ return sqrt(v); }
/*META @meta: label=Distort; @a: subtype=Vector; @b: subtype=Vector; */
vec3 vec3_distort(vec3 a, vec3 b, float fac) { return distort(a,b,fac); }

/*META @meta: label=Round; @v: subtype=Vector;*/
vec3 vec3_round(vec3 v){ return round(v); }
/*META @meta: label=Fraction; @v: subtype=Vector;*/
vec3 vec3_fract(vec3 v){ return fract(v); }
/*META @meta: label=Floor; @v: subtype=Vector;*/
vec3 vec3_floor(vec3 v){ return floor(v); }
/*META @meta: label=Ceil; @v: subtype=Vector;*/
vec3 vec3_ceil(vec3 v){ return ceil(v); }
/*META @meta: label=Snap; @a: subtype=Vector; @b: subtype=Vector; */
vec3 vec3_snap(vec3 a, vec3 b){ return snap(a,b); }

/*META @meta: label=Clamp; @v: subtype=Vector; @min: subtype=Vector; @max: subtype=Vector;*/
vec3 vec3_clamp(vec3 v, vec3 min, vec3 max){ return clamp(v, min, max); }

/*META @meta: label=Sign; @v: subtype=Vector;*/
vec3 vec3_sign(vec3 v){ return sign(v); }
/*META @meta: label=Absolute; @v: subtype=Vector;*/
vec3 vec3_abs(vec3 v){ return abs(v); }
/*META @meta: label=Min; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_min(vec3 a, vec3 b){ return min(a,b); }
/*META @meta: label=Max; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_max(vec3 a, vec3 b){ return max(a,b); }

/*META @meta: label=Mix 3D; @a: subtype=Vector; @b: subtype=Vector; @factor: subtype=Vector;*/
vec3 vec3_mix(vec3 a, vec3 b, vec3 factor){ return mix(a,b,factor); }
/*META @meta: label=Mix; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_mix_float(vec3 a, vec3 b, float factor){ return mix(a,b,factor); }

/*META @meta: label=Normalize; @v: subtype=Vector;*/
vec3 vec3_normalize(vec3 v){ return normalize(v); }

/*META @meta: label=Length; @v: subtype=Vector;*/
float vec3_length(vec3 v){ return length(v); }
/*META @meta: label=Distance; @a: subtype=Vector; @b: subtype=Vector;*/
float vec3_distance(vec3 a, vec3 b){ return distance(a,b); }
/*META @meta: label=Dot Product; @a: subtype=Vector; @b: subtype=Vector;*/
float vec3_dot_product(vec3 a, vec3 b){ return dot(a,b); }
/*META @meta: label=Cross Product; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_cross_product(vec3 a, vec3 b){ return cross(a,b); }
/*META @meta: label=Reflect; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_reflect(vec3 a, vec3 b){ return reflect(a,b); }
/*META @meta: label=Refract; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 vec3_refract(vec3 a, vec3 b, float ior){ return refract(a,normalize(b),ior); }
/*META @meta: label=Faceforward; @a: subtype=Vector; @b: subtype=Vector; @c: subtype=Vector; */
vec3 vec3_faceforward(vec3 a, vec3 b, vec3 c){ return faceforward(a,b,c); }

/* META @meta: label=Sine; @v: subtype=Vector; */
vec3 vec3_sin(vec3 v) { return sin(v); }
/* META @meta: label=Cosine; @v: subtype=Vector; */
vec3 vec3_cos(vec3 v) { return cos(v); }
/* META @meta: label=Tangent; @v: subtype=Vector; */
vec3 vec3_tan(vec3 v) { return tan(v); }

/*META @meta: label=Equal; @a: subtype=Vector; @b: subtype=Vector;*/
bool vec3_equal(vec3 a, vec3 b){ return a == b; }
/*META @meta: label=Not Equal; @a: subtype=Vector; @b: subtype=Vector;*/
bool vec3_not_equal(vec3 a, vec3 b){ return a != b; }

/*META @meta: label=If Else; @if_true: subtype=Vector; @if_false: subtype=Vector;*/
vec3 vec3_if_else(bool condition, vec3 if_true, vec3 if_false){ return condition ? if_true : if_false; }

/* META @meta: label=Join; */ 
vec3 vec3_join(float x, float y, float z) { return vec3(x,y,z);}
/*META @meta: label=Split; @v: subtype=Vector;*/
void vec3_split(vec3 v, out float x, out float y, out float z){ x=v.x; y=v.y; z=v.z; }

/*META @meta: subcategory=Map Range; label=Vector 3D; 
    @clamped: default=true;
    @value: default = 'vec3(0.5)';
    @from_min: subtype=Vector; default = vec3(0.0);
    @from_max: subtype=Vector; default = vec3(1.0);
    @to_min: subtype=Vector; default = vec3(0.0);
    @to_max: subtype=Vector; default = vec3(1.0);
*/
vec3 vec3_map_range(bool clamped, vec3 value, vec3 from_min, vec3 from_max, vec3 to_min, vec3 to_max)
{
    if(clamped)
    {
        return map_range_clamped(value, from_min, from_max, to_min, to_max);
    }else
    {
        return map_range(value, from_min, from_max, to_min, to_max);
    }
}

#endif //VEC3_GLSL
