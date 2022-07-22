#ifndef VEC2_GLSL
#define VEC2_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Vector 2D;
*/

/* META @meta: label=Add; */
vec2 vec2_add(vec2 a, vec2 b){ return a+b; }
/* META @meta: label=Subtract; */
vec2 vec2_subtract(vec2 a, vec2 b){ return a-b; }
/* META @meta: label=Multiply; */
vec2 vec2_multiply(vec2 a, vec2 b){ return a*b; }
/* META @meta: label=Divide; */
vec2 vec2_divide(vec2 a, vec2 b){ return a/b; }
/* META @meta: label=Scale; */
vec2 vec2_scale(vec2 v, float s){ return v*s; }
/* META @meta: label=Modulo; */
vec2 vec2_modulo(vec2 a, vec2 b){ return mod(a,b); }
/* META @meta: label=Power; */
vec2 vec2_pow(vec2 v, vec2 e){ return pow(v, e); }
/* META @meta: label=Square Root; */
vec2 vec2_sqrt(vec2 v){ return sqrt(v); }
/* META @meta: label=Distort; */
vec2 vec2_distort(vec2 a, vec2 b, float fac) { return distort(a,b,fac); }

/* META @meta: label=Round; */
vec2 vec2_round(vec2 v){ return round(v); }
/* META @meta: label=Fraction; */
vec2 vec2_fract(vec2 v){ return fract(v); }
/* META @meta: label=Floor; */
vec2 vec2_floor(vec2 v){ return floor(v); }
/* META @meta: label=Ceil; */
vec2 vec2_ceil(vec2 v){ return ceil(v); }
/* META @meta: label=Snap; */
vec2 vec2_snap(vec2 a, vec2 b){ return snap(a,b);}

/* META @meta: label=Clamp; */
vec2 vec2_clamp(vec2 v, vec2 min, vec2 max){ return clamp(v, min, max); }

/* META @meta: label=Sign; */
vec2 vec2_sign(vec2 v){ return sign(v); }
/* META @meta: label=Absolute; */
vec2 vec2_abs(vec2 v){ return abs(v); }
/* META @meta: label=Min; */
vec2 vec2_min(vec2 a, vec2 b){ return min(a,b); }
/* META @meta: label=Max; */
vec2 vec2_max(vec2 a, vec2 b){ return max(a,b); }

/* META @meta: label=Mix 2D; */
vec2 vec2_mix(vec2 a, vec2 b, vec2 factor){ return mix(a,b,factor); }
/* META @meta: label=Mix; */
vec2 vec2_mix_float(vec2 a, vec2 b, float factor){ return mix(a,b,factor); }

/* META @meta: label=Normalize; */
vec2 vec2_normalize(vec2 v){ return normalize(v); }

/* META @meta: label=Length; */
float vec2_length(vec2 v){ return length(v); }
/* META @meta: label=Distance; */
float vec2_distance(vec2 a, vec2 b){ return distance(a,b); }
/* META @meta: label=Dot Product; */
float vec2_dot_product(vec2 a, vec2 b){ return dot(a,b); }

/* META @meta: label=Sine; */
vec2 vec2_sin(vec2 v) { return sin(v); }
/* META @meta: label=Cosine; */
vec2 vec2_cos(vec2 v) { return cos(v); }
/* META @meta: label=Tangent; */
vec2 vec2_tan(vec2 v) { return tan(v); }
/* META @meta: label=Angle; */
float vec2_angle(vec2 a, vec2 b) { return vector_angle(a, b); }

/* META @meta: label=Equal; */
bool vec2_equal(vec2 a, vec2 b){ return a == b; }
/* META @meta: label=Not Equal; */
bool vec2_not_equal(vec2 a, vec2 b){ return a != b; }

/* META @meta: label=If Else; */
vec2 vec2_if_else(bool condition, vec2 if_true, vec2 if_false){ return condition ? if_true : if_false; }

/* META @meta: label=Join; */
vec2 vec2_join(float x, float y) { return vec2(x,y);}
/* META @meta: label=Split; */
void vec2_split(vec2 v, out float x, out float y){ x=v.x; y=v.y; }

/*META @meta: subcategory=Map Range; label=Vector 2D; 
    @clamped: default=true;
    @value: default = 'vec2(0.5)';
    @from_min: default = vec2(0.0);
    @from_max: default = vec2(1.0);
    @to_min: default = vec2(0.0);
    @to_max: default = vec2(1.0);
*/
vec2 vec2_map_range(bool clamped, vec2 value, vec2 from_min, vec2 from_max, vec2 to_min, vec2 to_max)
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

#endif //VEC2_GLSL
