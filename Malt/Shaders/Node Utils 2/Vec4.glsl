#ifndef NODE_UTILS_2_VEC4_GLSL
#define NODE_UTILS_2_VEC4_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Vector 4D;
*/

/*META @meta: label=Add; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 Vec4_add(vec4 a, vec4 b){ return a+b; }
/*META @meta: label=Subtract; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 Vec4_subtract(vec4 a, vec4 b){ return a-b; }
/*META @meta: label=Multiply; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 Vec4_multiply(vec4 a, vec4 b){ return a*b; }
/*META @meta: label=Divide; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 Vec4_divide(vec4 a, vec4 b){ return a/b; }
/*META @meta: label=Scale; @a: subtype=Vector;*/
vec4 Vec4_scale(vec4 a, float fac){ return a*fac; }
/*META 
    @meta: label=Map Range; 
    @clamped: default=true;
    @a: label=Vector; default = 'vec4(0.5)';
    @from_min: subtype=Vector; default = vec4(0.0);
    @from_max: subtype=Vector; default = vec4(1.0);
    @to_min: subtype=Vector; default = vec4(0.0);
    @to_max: subtype=Vector; default = vec4(1.0);
*/
vec4 Vec4_map_range(bool clamped, vec4 a, vec4 from_min, vec4 from_max, vec4 to_min, vec4 to_max)
{
    if(clamped)
    {
        return map_range_clamped(a, from_min, from_max, to_min, to_max);
    }
    else
    {
        return map_range(a, from_min, from_max, to_min, to_max);
    }
}
/*META @meta: label=Modulo; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 Vec4_modulo(vec4 a, vec4 b){ return mod(a,b); }
/*META @meta: label=Power; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 Vec4_pow(vec4 a, vec4 b){ return pow(a, b); }
/*META @meta: label=Square Root; @a: subtype=Vector;*/
vec4 Vec4_sqrt(vec4 a){ return sqrt(a); }
/*META @meta: label=Distort; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 Vec4_distort(vec4 a, vec4 b, float fac) { return distort(a,b,fac); }

/*META @meta: label=Round; @a: subtype=Vector;*/
vec4 Vec4_round(vec4 a){ return round(a); }
/*META @meta: label=Fraction; @a: subtype=Vector;*/
vec4 Vec4_fract(vec4 a){ return fract(a); }
/*META @meta: label=Floor; @a: subtype=Vector;*/
vec4 Vec4_floor(vec4 a){ return floor(a); }
/*META @meta: label=Ceil; @a: subtype=Vector;*/
vec4 Vec4_ceil(vec4 a){ return ceil(a); }

/*META @meta: label=Clamp; @a: subtype=Vector; @b: label=Min; subtype=Vector; @c: label=Max; subtype=Vector;*/
vec4 Vec4_clamp(vec4 a, vec4 b, vec4 c){ return clamp(a, b, c); }

/*META @meta: label=Sign; @a: subtype=Vector;*/
vec4 Vec4_sign(vec4 a){ return sign(a); }
/*META @meta: label=Absolute; @a: subtype=Vector;*/
vec4 Vec4_abs(vec4 a){ return abs(a); }
/*META @meta: label=Min; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 Vec4_min(vec4 a, vec4 b){ return min(a,b); }
/*META @meta: label=Max; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 Vec4_max(vec4 a, vec4 b){ return max(a,b); }

/*META @meta: label=Mix 4D; @a: subtype=Vector; @b: subtype=Vector; @c: label=Factor; subtype=Vector;*/
vec4 Vec4_mix(vec4 a, vec4 b, vec4 c){ return safe_mix(a,b,c); }
/*META @meta: label=Mix; @a: subtype=Vector; @b: subtype=Vector;*/
vec4 Vec4_mix_float(vec4 a, vec4 b, float fac){ return safe_mix(a,b,fac); }

/*META @meta: label=Normalize; @a: subtype=Vector;*/
vec4 Vec4_normalize(vec4 a){ return a != vec4(0) ? normalize(a) : vec4(0); }

/*META @meta: label=Length; @a: subtype=Vector;*/
float Vec4_length(vec4 a){ return a != vec4(0) ? length(a) : 0; }
/*META @meta: label=Distance; @a: subtype=Vector; @b: subtype=Vector;*/
float Vec4_distance(vec4 a, vec4 b){ return a != b ? distance(a,b) : 0; }
/*META @meta: label=Dot Product; @a: subtype=Vector; @b: subtype=Vector;*/
float Vec4_dot_product(vec4 a, vec4 b){ return dot(a,b); }

/* META @meta: label=Sine; @a: subtype=Vector; */
vec4 Vec4_sin(vec4 a) { return sin(a); }
/* META @meta: label=Cosine; @a: subtype=Vector; */
vec4 Vec4_cos(vec4 a) { return cos(a); }
/* META @meta: label=Tangent; @a: subtype=Vector; */
vec4 Vec4_tan(vec4 a) { return tan(a); }
/* META @meta: label=Angle; @a: subtype=Vector; @b: subtype=Vector; */
float Vec4_angle(vec4 a, vec4 b) { return vector_angle(a, b); }

/*META @meta: label=Equal; @a: subtype=Vector; @b: subtype=Vector;*/
bool Vec4_equal(vec4 a, vec4 b){ return a == b; }
/*META @meta: label=Not Equal; @a: subtype=Vector; @b: subtype=Vector;*/
bool Vec4_not_equal(vec4 a, vec4 b){ return a != b; }

/*META @a: label=If True; subtype=Vector; @b: label=If False; subtype=Vector;*/
vec4 Vec4_if_else(bool condition, vec4 a, vec4 b){ return condition ? a : b; }

/*META @meta: label=Combine; */
vec4 Vec4_combine(float r, float g, float b, float a) { return vec4(r,g,b,a);}
/* META @meta: label=Combine Color; @c: subtype=Color; @a: subtype=Slider; min=0.0; max=1.0; default=1.0;*/
vec4 Vec4_combine_color(vec3 c, float a){ return vec4(c, a); }
/*META @meta: label=Separate; @a: subtype=Vector; @w: label=A;*/
void Vec4_separate(vec4 a, out float r, out float g, out float b, out float w){ r=a.r; g=a.g; b=a.b; w=a.a; }
/*META @meta: label=Separate Color; @a: subtype=Color; @w: label=A; */
void Vec4_separate_color(vec4 a, out vec3 c, out float w){ c=a.xyz; w=a.a; }

#endif //NODE_UTILS_2_VEC4_GLSL
