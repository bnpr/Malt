#ifndef NODE_UTILS_2_VEC3_GLSL
#define NODE_UTILS_2_VEC3_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Vector 3D;
*/

/*META @meta: label=Add; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 Vec3_add(vec3 a, vec3 b){ return a+b; }
/*META @meta: label=Subtract; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 Vec3_subtract(vec3 a, vec3 b){ return a-b; }
/*META @meta: label=Multiply; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 Vec3_multiply(vec3 a, vec3 b){ return a*b; }
/*META @meta: label=Divide; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 Vec3_divide(vec3 a, vec3 b){ return a/b; }
/*META @meta: label=Scale; @a: subtype=Vector;*/
vec3 Vec3_scale(vec3 a, float fac){ return a*fac; }
/*META 
    @meta: label=Map Range;
    @clamped: default=true;
    @a: label=Vector; default = 'vec3(0.5)';
    @from_min: subtype=Vector; default = vec3(0.0);
    @from_max: subtype=Vector; default = vec3(1.0);
    @to_min: subtype=Vector; default = vec3(0.0);
    @to_max: subtype=Vector; default = vec3(1.0);
*/
vec3 Vec3_map_range(bool clamped, vec3 a, vec3 from_min, vec3 from_max, vec3 to_min, vec3 to_max)
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
vec3 Vec3_modulo(vec3 a, vec3 b){ return mod(a,b); }
/*META @meta: label=Power; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 Vec3_pow(vec3 a, vec3 b){ return pow(a, b); }
/*META @meta: label=Square Root; @a: subtype=Vector;*/
vec3 Vec3_sqrt(vec3 a){ return sqrt(a); }
/*META @meta: label=Distort; @a: subtype=Vector; @b: subtype=Vector; */
vec3 Vec3_distort(vec3 a, vec3 b, float fac) { return distort(a,b,fac); }

/*META @meta: label=Round; @a: subtype=Vector;*/
vec3 Vec3_round(vec3 a){ return round(a); }
/*META @meta: label=Fraction; @a: subtype=Vector;*/
vec3 Vec3_fract(vec3 a){ return fract(a); }
/*META @meta: label=Floor; @a: subtype=Vector;*/
vec3 Vec3_floor(vec3 a){ return floor(a); }
/*META @meta: label=Ceil; @a: subtype=Vector;*/
vec3 Vec3_ceil(vec3 a){ return ceil(a); }
/*META @meta: label=Snap; @a: subtype=Vector; @b: subtype=Vector; */
vec3 Vec3_snap(vec3 a, vec3 b){ return snap(a,b); }

/*META @meta: label=Clamp; @a: subtype=Vector; @b: label=Min; subtype=Vector; @c: label=Max; subtype=Vector;*/
vec3 Vec3_clamp(vec3 a, vec3 b, vec3 c){ return clamp(a, b, c); }

/*META @meta: label=Sign; @a: subtype=Vector;*/
vec3 Vec3_sign(vec3 a){ return sign(a); }
/*META @meta: label=Absolute; @a: subtype=Vector;*/
vec3 Vec3_abs(vec3 a){ return abs(a); }
/*META @meta: label=Min; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 Vec3_min(vec3 a, vec3 b){ return min(a,b); }
/*META @meta: label=Max; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 Vec3_max(vec3 a, vec3 b){ return max(a,b); }

/*META @meta: label=Mix 3D; @a: subtype=Vector; @b: subtype=Vector; @c: label=Factor; subtype=Vector;*/
vec3 Vec3_mix(vec3 a, vec3 b, vec3 c){ return safe_mix(a,b,c); }
/*META @meta: label=Mix; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 Vec3_mix_float(vec3 a, vec3 b, float fac){ return safe_mix(a,b,fac); }

/*META @meta: label=Normalize; @a: subtype=Vector;*/
vec3 Vec3_normalize(vec3 a){ return a != vec3(0) ? normalize(a) : vec3(0); }

/*META @meta: label=Length; @a: subtype=Vector;*/
float Vec3_length(vec3 a){ return a != vec3(0) ? length(a) : 0; }
/*META @meta: label=Distance; @a: subtype=Vector; @b: subtype=Vector;*/
float Vec3_distance(vec3 a, vec3 b){ return a != b ? distance(a,b) : 0; }
/*META @meta: label=Dot Product; @a: subtype=Vector; @b: subtype=Vector;*/
float Vec3_dot_product(vec3 a, vec3 b){ return dot(a,b); }
/*META @meta: label=Cross Product; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 Vec3_cross_product(vec3 a, vec3 b){ return cross(a,b); }
/*META @meta: label=Reflect; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 Vec3_reflect(vec3 a, vec3 b){ return reflect(a,b); }
/*META @meta: label=Refract; @a: subtype=Vector; @b: subtype=Vector;*/
vec3 Vec3_refract(vec3 a, vec3 b, float ior){ return refract(a,normalize(b),ior); }
/*META @meta: label=Faceforward; @a: subtype=Vector; @b: subtype=Vector; @c: subtype=Vector; */
vec3 Vec3_faceforward(vec3 a, vec3 b, vec3 c){ return faceforward(a,b,c); }

/* META @meta: label=Sine; @a: subtype=Vector; */
vec3 Vec3_sin(vec3 a) { return sin(a); }
/* META @meta: label=Cosine; @a: subtype=Vector; */
vec3 Vec3_cos(vec3 a) { return cos(a); }
/* META @meta: label=Tangent; @a: subtype=Vector; */
vec3 Vec3_tan(vec3 a) { return tan(a); }
/* META @meta: label=Rotate Euler; @a: subtype=Vector; @euler: subtype=Euler; */
vec3 Vec3_rotate_euler(vec3 a, vec3 euler, bool invert)
{
    mat4 m = mat4_rotation_from_euler(euler);
    if(invert)
    {
        m = inverse(m);
    }
    return transform_point(m, a);
}
/* META @meta: label=Rotate Axis Angle; @a: subtype=Vector; @b: label=Axis; subtype=Vector; default=vec3(0.0, 0.0, 1.0); */
vec3 Vec3_rotate_axis_angle(vec3 a, vec3 b, float angle) 
{ 
    mat4 m = mat4_rotation_from_quaternion(quaternion_from_axis_angle(b, angle));
    return transform_point(m, a);
}
/* META @meta: label=Angle; @a: subtype=Vector; @b: subtype=Vector; */
float Vec3_angle(vec3 a, vec3 b) { return vector_angle(a, b); }

/*META @meta: label=Equal; @a: subtype=Vector; @b: subtype=Vector;*/
bool Vec3_equal(vec3 a, vec3 b){ return a == b; }
/*META @meta: label=Not Equal; @a: subtype=Vector; @b: subtype=Vector;*/
bool Vec3_not_equal(vec3 a, vec3 b){ return a != b; }

/*META @meta: label=If Else; @a: label=If True; subtype=Vector; @b: label=If False; subtype=Vector;*/
vec3 Vec3_if_else(bool condition, vec3 a, vec3 b){ return condition ? a : b; }

/* META @meta: label=Combine; */
vec3 Vec3_combine(float x, float y, float z) { return vec3(x,y,z);}
/*META @meta: label=Separate; @a: subtype=Vector;*/
void Vec3_separate(vec3 a, out float x, out float y, out float z){ x=a.x; y=a.y; z=a.z; }

#endif //NODE_UTILS_2_VEC3_GLSL
