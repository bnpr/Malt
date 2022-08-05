#ifndef VEC4_GLSL
#define VEC4_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=4D Math;
*/

/*META @meta: label=Add; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_add(vec4 a, vec4 b){ return a+b; }
/*META @meta: label=Subtract; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_subtract(vec4 a, vec4 b){ return a-b; }
/*META @meta: label=Multiply; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_multiply(vec4 a, vec4 b){ return a*b; }
/*META @meta: label=Divide; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_divide(vec4 a, vec4 b){ return a/b; }
/*META @meta: label=Scale; @v: subtype=Vector;*/
vec4 vec4_scale(vec4 v, float s){ return v*s; }
/*META @meta: label=Modulo; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_modulo(vec4 a, vec4 b){ return mod(a,b); }
/*META @meta: label=Power; @v: subtype=Vector; @e: subtype=Vector;*/
vec4 vec4_pow(vec4 v, vec4 e){ return pow(v, e); }
/*META @meta: label=Square Root; @v: subtype=Vector;*/
vec4 vec4_sqrt(vec4 v){ return sqrt(v); }
/*META @meta: label=Distort; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_distort(vec4 a, vec4 b, float fac) { return distort(a,b,fac); }

/*META @meta: label=Round; @v: subtype=Vector;*/
vec4 vec4_round(vec4 v){ return round(v); }
/*META @meta: label=Fraction; @v: subtype=Vector;*/
vec4 vec4_fract(vec4 v){ return fract(v); }
/*META @meta: label=Floor; @v: subtype=Vector;*/
vec4 vec4_floor(vec4 v){ return floor(v); }
/*META @meta: label=Ceil; @v: subtype=Vector;*/
vec4 vec4_ceil(vec4 v){ return ceil(v); }

/*META @meta: label=Clamp; @v: subtype=Vector; @min: subtype=Vector; @max: subtype=Vector;*/
vec4 vec4_clamp(vec4 v, vec4 min, vec4 max){ return clamp(v, min, max); }

/*META @meta: label=Sign; @v: subtype=Vector;*/
vec4 vec4_sign(vec4 v){ return sign(v); }
/*META @meta: label=Absolute; @v: subtype=Vector;*/
vec4 vec4_abs(vec4 v){ return abs(v); }
/*META @meta: label=Min; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_min(vec4 a, vec4 b){ return min(a,b); }
/*META @meta: label=Max; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_max(vec4 a, vec4 b){ return max(a,b); }

/*META @meta: label=Mix 4D; @a: subtype=Vector; @b: subtype=Vector; @factor: subtype=Vector;*/
vec4 vec4_mix(vec4 a, vec4 b, vec4 factor){ return mix(a,b,factor); }
/*META @meta: label=Mix; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 vec4_mix_float(vec4 a, vec4 b, float factor){ return mix(a,b,factor); }

/*META @meta: label=Normalize; @v: subtype=Vector;*/
vec4 vec4_normalize(vec4 v){ return normalize(v); }

/*META @meta: label=Length; @v: subtype=Vector;*/
float vec4_length(vec4 v){ return length(v); }
/*META @meta: label=Distance; @a: subtype=Vector; @b: subtype=Vector;*/
float vec4_distance(vec4 a, vec4 b){ return distance(a,b); }
/*META @meta: label=Dot Product; @a: subtype=Vector; @b: subtype=Vector;*/
float vec4_dot_product(vec4 a, vec4 b){ return dot(a,b); }

/* META @meta: label=Sine; @v: subtype=Vector; */
vec4 vec4_sin(vec4 v) { return sin(v); }
/* META @meta: label=Cosine; @v: subtype=Vector; */
vec4 vec4_cos(vec4 v) { return cos(v); }
/* META @meta: label=Tangent; @v: subtype=Vector; */
vec4 vec4_tan(vec4 v) { return tan(v); }
/* META @meta: label=Angle; @a: subtype=Vector; @b: subtype=Vector; */
float vec4_angle(vec4 a, vec4 b) { return vector_angle(a, b); }

/*META @meta: label=Equal; @a: subtype=Vector; @b: subtype=Vector;*/
bool vec4_equal(vec4 a, vec4 b){ return a == b; }
/*META @meta: label=Not Equal; @a: subtype=Vector; @b: subtype=Vector;*/
bool vec4_not_equal(vec4 a, vec4 b){ return a != b; }

/*META @if_true: subtype=Vector; @if_false: subtype=Vector;*/
vec4 vec4_if_else(bool condition, vec4 if_true, vec4 if_false){ return condition ? if_true : if_false; }

/*META @meta: label=Join; */
vec4 vec4_join(float r, float g, float b, float a) { return vec4(r,g,b,a);}
/*META @meta: label=Split; @v: subtype=Vector;*/
void vec4_split(vec4 v, out float r, out float g, out float b, out float a){ r=v.r; g=v.g; b=v.b; a=v.a; }

/*META @meta: subcategory=Map Range; label=Vector 4D; 
    @clamped: default=true;
    @value: default = 'vec4(0.5)';
    @from_min: subtype=Vector; default = vec4(0.0);
    @from_max: subtype=Vector; default = vec4(1.0);
    @to_min: subtype=Vector; default = vec4(0.0);
    @to_max: subtype=Vector; default = vec4(1.0);
*/
vec4 vec3_map_range(bool clamped, vec4 value, vec4 from_min, vec4 from_max, vec4 to_min, vec4 to_max)
{
    if(clamped)
    {
        return map_range_clamped(value, from_min, from_max, to_min, to_max);
    }
    else
    {
        return map_range(value, from_min, from_max, to_min, to_max);
    }
}

#endif //VEC4_GLSL
