#ifndef NODE_UTILS_2_VEC2_GLSL
#define NODE_UTILS_2_VEC2_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Vector 2D;
*/

/* META @meta: label=Add; */
vec2 Vec2_add(vec2 a, vec2 b){ return a+b; }
/* META @meta: label=Subtract; */
vec2 Vec2_subtract(vec2 a, vec2 b){ return a-b; }
/* META @meta: label=Multiply; */
vec2 Vec2_multiply(vec2 a, vec2 b){ return a*b; }
/* META @meta: label=Divide; */
vec2 Vec2_divide(vec2 a, vec2 b){ return a/b; }
/* META @meta: label=Scale; */
vec2 Vec2_scale(vec2 a, float fac){ return a*fac; }
/*META 
    @meta: label=Map Range; 
    @clamped: default=true;
    @a: label=UV; default = 'vec2(0.5)';
    @from_min: default = vec2(0.0);
    @from_max: default = vec2(1.0);
    @to_min: default = vec2(0.0);
    @to_max: default = vec2(1.0);
*/
vec2 Vec2_map_range(bool clamped, vec2 a, vec2 from_min, vec2 from_max, vec2 to_min, vec2 to_max)
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
/* META @meta: label=Modulo; */
vec2 Vec2_modulo(vec2 a, vec2 b){ return mod(a,b); }
/* META @meta: label=Power; */
vec2 Vec2_pow(vec2 a, vec2 b){ return pow(a, b); }
/* META @meta: label=Square Root; */
vec2 Vec2_sqrt(vec2 a){ return sqrt(a); }
/* META @meta: label=Distort; */
vec2 Vec2_distort(vec2 a, vec2 b, float fac) { return distort(a,b,fac); }

/* META @meta: label=Round; */
vec2 Vec2_round(vec2 a){ return round(a); }
/* META @meta: label=Fraction; */
vec2 Vec2_fract(vec2 a){ return fract(a); }
/* META @meta: label=Floor; */
vec2 Vec2_floor(vec2 a){ return floor(a); }
/* META @meta: label=Ceil; */
vec2 Vec2_ceil(vec2 a){ return ceil(a); }
/* META @meta: label=Snap; */
vec2 Vec2_snap(vec2 a, vec2 b){ return snap(a,b);}

/* META @meta: label=Clamp; @b: label=Min; @c: label=Max; */
vec2 Vec2_clamp(vec2 a, vec2 b, vec2 c){ return clamp(a, b, c); }

/* META @meta: label=Sign; */
vec2 Vec2_sign(vec2 a){ return sign(a); }
/* META @meta: label=Absolute; */
vec2 Vec2_abs(vec2 a){ return abs(a); }
/* META @meta: label=Min; */
vec2 Vec2_min(vec2 a, vec2 b){ return min(a,b); }
/* META @meta: label=Max; */
vec2 Vec2_max(vec2 a, vec2 b){ return max(a,b); }

/* META @meta: label=Mix 2D; @c: label=Factor; */
vec2 Vec2_mix(vec2 a, vec2 b, vec2 c){ return safe_mix(a,b,c); }
/* META @meta: label=Mix; */
vec2 Vec2_mix_float(vec2 a, vec2 b, float fac){ return safe_mix(a,b,fac); }

/* META @meta: label=Normalize; */
vec2 Vec2_normalize(vec2 a){ return a != vec2(0) ? normalize(a) : vec2(0); }

/* META @meta: label=Length; */
float Vec2_length(vec2 a){ return a != vec2(0) ? length(a) : 0; }
/* META @meta: label=Distance; */
float Vec2_distance(vec2 a, vec2 b){ return a != b ? distance(a,b) : 0; }
/* META @meta: label=Dot Product; */
float Vec2_dot_product(vec2 a, vec2 b){ return dot(a,b); }

/* META @meta: label=Sine; */
vec2 Vec2_sin(vec2 a) { return sin(a); }
/* META @meta: label=Cosine; */
vec2 Vec2_cos(vec2 a) { return cos(a); }
/* META @meta: label=Tangent; */
vec2 Vec2_tan(vec2 a) { return tan(a); }
/* META @meta: label=Rotate; */
vec2 Vec2_rotate(vec2 a, float angle) { return rotate_2d(a, angle); }
/* META @meta: label=Angle; */
float Vec2_angle(vec2 a, vec2 b) { return vector_angle(a, b); }

/* META @meta: label=Equal; */
bool Vec2_equal(vec2 a, vec2 b){ return a == b; }
/* META @meta: label=Not Equal; */
bool Vec2_not_equal(vec2 a, vec2 b){ return a != b; }

/* META @meta: label=If Else; @a: label=If True; @b: label=If False; */
vec2 Vec2_if_else(bool condition, vec2 a, vec2 b){ return condition ? a : b; }

/* META @meta: label=Combine; */
vec2 Vec2_combine(float x, float y) { return vec2(x,y);}
/* META @meta: label=Separate; */
void Vec2_separate(vec2 a, out float x, out float y){ x=a.x; y=a.y; }

#endif //NODE_UTILS_2_VEC2_GLSL
