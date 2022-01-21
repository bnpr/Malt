#ifndef COMMON_QUATERNION_GLSL
#define COMMON_QUATERNION_GLSL

/*  META
    @axis: subtype=Normal;
    @angle: subtype=Angle; default=0;
*/
vec4 quaternion_from_axis_angle(vec3 axis, float angle)
{
    return vec4(axis * sin(0.5 * angle), cos(0.5 * angle));
}

/*  META
    @from: subtype=Normal;
    @to: subtype=Normal;
*/
vec4 quaternion_from_vector_delta(vec3 from, vec3 to)
{
    return normalize(vec4(cross(from, to), 1.0 + dot(from, to)));
}

/*  META
    @quaternion: subtype=Quaternion; default=vec4(0,0,0,1);
*/
vec4 quaternion_inverted(vec4 quaternion)
{ 
    return vec4(-quaternion.xyz, quaternion.w);
}

/*  META
    @a: subtype=Quaternion; default=vec4(0,0,0,1);
    @b: subtype=Quaternion; default=vec4(0,0,0,1);
*/
vec4 quaternion_multiply(vec4 a, vec4 b) 
{
    return vec4
    (
        a.xyz * b.w + b.xyz * a.w + cross(a.xyz, b.xyz),
        a.w * b.w - dot(a.xyz, b.xyz)
    );
}

/*  META
    @quaternion: subtype=Quaternion; default=vec4(0,0,0,1);
    @vector: subtype=Vector; default=vec3(0);
*/
vec3 quaternion_transform(vec4 quaternion, vec3 vector)
{
    vec3 t = cross(quaternion.xyz, vector) * 2.0;
    return vector + t * quaternion.w + cross(quaternion.xyz, t);
}

/*  META
    @a: subtype=Quaternion; default=vec4(0,0,0,1);
    @b: subtype=Quaternion; default=vec4(0,0,0,1);
    @factor: subtype=Slider; default=0.5; min=0; max=1;
*/
vec4 quaternion_mix(vec4 a, vec4 b, float factor)
{
    return normalize(mix(a, b, factor));
}

#endif //COMMON_QUATERION_GLSL
