//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef COMMON_QUATERNION_GLSL
#define COMMON_QUATERNION_GLSL

//axis should be normalized
vec4 quaternion_from_axis_angle(vec3 axis, float angle)
{
    return vec4(axis * sin(0.5 * angle), cos(0.5 * angle));
}

//vectors should be normalized
vec4 quaternion_from_vector_delta(vec3 from, vec3 to)
{
    return normalize(vec4(cross(from, to), 1.0 + dot(from, to)));
}

vec4 quaternion_inverted(vec4 quaternion)
{ 
    return vec4(-quaternion.xyz, quaternion.w);
}

vec4 quaternion_multiply(vec4 a, vec4 b) 
{
    return vec4
    (
        a.xyz * b.w + b.xyz * a.w + cross(a.xyz, b.xyz),
        a.w * b.w - dot(a.xyz, b.xyz)
    );
}

vec3 quaternion_transform(vec4 quaternion, vec3 vector)
{
    vec3 t = cross(quaternion.xyz, vector) * 2.0;
    return vector + t * quaternion.w + cross(quaternion.xyz, t);
}

vec4 quaternion_mix(vec4 a, vec4 b, float factor)
{
    return normalize(mix(a, b, factor));
}

#endif //COMMON_QUATERION_GLSL
