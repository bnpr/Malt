#ifndef COMMON_MATRIX_GLSL
#define COMMON_MATRIX_GLSL

/* META GLOBAL
    @meta: category=Vector;
*/

#include "Common/Quaternion.glsl"

/*  META
    @t: subtype=Vector;
*/
mat4 mat4_translation(vec3 t)
{
    mat4 m = mat4(1.0);
    m[3] = vec4(t, 1);
    return m;
}

/*  META
    @q: subtype=Quaternion; default=vec4(0,0,0,1);
*/
mat4 mat4_rotation_from_quaternion(vec4 q)
{
    return mat4(mat3(
        quaternion_transform(q, vec3(1,0,0)),
        quaternion_transform(q, vec3(0,1,0)),
        quaternion_transform(q, vec3(0,0,1))
    ));
}

/*  META
    @e: subtype=Euler;
*/
mat4 mat4_rotation_from_euler(vec3 e)
{
    mat4 x = mat4_rotation_from_quaternion(quaternion_from_axis_angle(vec3(1,0,0), e.x));
    mat4 y = mat4_rotation_from_quaternion(quaternion_from_axis_angle(vec3(0,1,0), e.y));
    mat4 z = mat4_rotation_from_quaternion(quaternion_from_axis_angle(vec3(0,0,1), e.z));

    return z * y * x;
}

/*  META
    @s: subtype=Vector; default=vec3(1);
*/
mat4 mat4_scale(vec3 s)
{
    return mat4(mat3(s.x,0,0, 0,s.y,0, 0,0,s.z));
}

/*  META
    @matrix: default=mat4(1);
*/
bool is_ortho(mat4 matrix)
{
    return matrix[3][3] == 1.0;
}

#endif // COMMON_MATRIX_GLSL
