//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef COMMON_TRANSFORM_GLSL
#define COMMON_TRANSFORM_GLSL

#include "Common.glsl"

vec3 transform_point(mat4 matrix, vec3 point)
{
    return (matrix * vec4(point, 1.0)).xyz;
}

vec3 project_point(mat4 matrix, vec3 point)
{
    vec4 result = matrix * vec4(point, 1.0);
    return result.xyz / result.w;
}

vec3 transform_direction(mat4 matrix, vec3 direction)
{
    return mat3(matrix) * direction;
}

vec3 transform_normal(mat4 matrix, vec3 normal)
{
    return normalize(transform_direction(matrix, normal));
}

vec3 camera_position()
{
    return transform_point(inverse(CAMERA), vec3(0,0,0));
}

vec3 model_position()
{
    return transform_point(MODEL, vec3(0,0,0));
}

bool is_ortho(mat4 matrix)
{
    return matrix[3][3] == 1.0;
}

#endif //COMMON_TRANSFORM_GLSL

