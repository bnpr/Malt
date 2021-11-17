//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#ifndef COMMON_MATRIX_GLSL
#define COMMON_MATRIX_GLSL

#include "Common/Quaternion.glsl"

mat4 mat4_translation(vec3 t)
{
    mat4 m = mat4(1.0);
    m[3] = vec4(t, 1);
    return m;
}

mat4 mat4_rotation(vec4 q)
{
    return mat4(mat3(
        quaternion_transform(q, vec3(1,0,0)),
        quaternion_transform(q, vec3(0,1,0)),
        quaternion_transform(q, vec3(0,0,1))
    ));
}

mat4 mat4_rotation(vec3 e)
{
    mat4 x = mat4_rotation(quaternion_from_axis_angle(vec3(1,0,0), e.x));
    mat4 y = mat4_rotation(quaternion_from_axis_angle(vec3(0,1,0), e.y));
    mat4 z = mat4_rotation(quaternion_from_axis_angle(vec3(0,0,1), e.z));

    return z * y * x;
}

mat4 mat4_scale(vec3 s)
{
    return mat4(mat3(s.x,0,0, 0,s.y,0, 0,0,s.z));
}

#endif // COMMON_MATRIX_GLSL
