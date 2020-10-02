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
    return (result.xyz / result.w) * sign(result.w);
}

vec3 transform_direction(mat4 matrix, vec3 direction)
{
    return mat3(matrix) * direction;
}

vec3 transform_normal(mat4 matrix, vec3 normal)
{
    return normalize(transform_direction(matrix, normal));
}

#ifdef PIXEL_SHADER

vec3 sample_normal_map_ex(sampler2D normal_texture, int uv_index, vec2 uv)
{
    vec3 tangent = texture(normal_texture, uv).xyz;
    tangent = tangent * 2.0 - 1.0;
    mat3 TBN = mat3(TANGENT[uv_index], BITANGENT[uv_index], NORMAL);
    if(!gl_FrontFacing)
    {
        TBN = mat3(TANGENT[uv_index], BITANGENT[uv_index], -NORMAL);
    }
    return normalize(TBN * tangent);
}

vec3 sample_normal_map(sampler2D normal_texture, int uv_index)
{
    return sample_normal_map_ex(normal_texture, uv_index, UV[uv_index]);
}

#endif //PIXEL_SHADER

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

vec3 view_direction()
{
    if (is_ortho(PROJECTION))
    {
        return transform_normal(inverse(CAMERA), vec3(0,0,1));
    }
    else
    {
        return normalize(camera_position() - POSITION);
    }
}

#ifdef PIXEL_SHADER

vec2 screen_uv()
{
    return vec2(gl_FragCoord) / vec2(RESOLUTION);
}

#endif //PIXEL_SHADER

vec3 screen_to_camera(vec2 uv, float depth)
{
    vec3 clip_position = vec3(uv, depth) * 2.0 - 1.0;
    vec4 camera_position = inverse(PROJECTION) * vec4(clip_position, 1.0);
    camera_position /= camera_position.w;

    return camera_position.xyz;
}

float depth_to_z(float depth)
{
    return screen_to_camera(vec2(0,0), depth).z;
}

#ifdef PIXEL_SHADER

float pixel_world_size_at(float depth)
{
    vec2 uv = screen_uv();
    vec2 offset = vec2(1.0 / RESOLUTION.x, 0);
    return distance(screen_to_camera(uv, depth), screen_to_camera(uv + offset, depth));
}

float pixel_world_size()
{
    return pixel_world_size_at(gl_FragCoord.z);
}

#endif //PIXEL_SHADER

vec2 matcap_uv(vec3 normal)
{
    vec3 r = cross(transform_normal(CAMERA, view_direction()), transform_normal(CAMERA, normal));
    vec2 uv = r.xy * 0.5 + 0.5;
    uv.xy = uv.yx;
    uv.y = 1.0 - uv.y;

    return uv;
}

vec2 hdri_uv(vec3 normal)
{
    vec2 uv = vec2(atan(normal.y, normal.x), asin(normal.z));
    vec2 inverse_atan = vec2(0.1591, 0.3183);
    return uv * inverse_atan + 0.5;
}

float ray_plane_intersection(vec3 ray_origin, vec3 ray_direction, vec3 plane_position, vec3 plane_normal)
{
    float r_direction = dot(ray_direction, plane_normal);
    float r_origin = dot(ray_origin, plane_normal);
    float p_position = dot(plane_position, plane_normal);

    return (p_position - r_origin) / r_direction;
}

#endif //COMMON_TRANSFORM_GLSL

