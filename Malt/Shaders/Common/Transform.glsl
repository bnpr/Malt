#ifndef COMMON_TRANSFORM_GLSL
#define COMMON_TRANSFORM_GLSL

#include "Common.glsl"

/*  META
    @matrix: default=mat4(1);
    @point: subtype=Vector;
*/
vec3 transform_point(mat4 matrix, vec3 point)
{
    return (matrix * vec4(point, 1.0)).xyz;
}

/*  META
    @matrix: default=mat4(1);
    @point: subtype=Vector;
*/
vec3 project_point(mat4 matrix, vec3 point)
{
    vec4 result = matrix * vec4(point, 1.0);
    return (result.xyz / result.w) * sign(result.w);
}

/*  META
    @matrix: default=mat4(1);
    @direction: subtype=Vector;
*/
vec3 transform_direction(mat4 matrix, vec3 direction)
{
    return mat3(matrix) * direction;
}

/*  META
    @matrix: default=mat4(1);
    @normal: subtype=Normal;
*/
vec3 transform_normal(mat4 matrix, vec3 normal)
{
    mat3 m = transpose(inverse(mat3(matrix)));
    return normalize(m * normal);
}

vec3 camera_position()
{
    return transform_point(inverse(CAMERA), vec3(0,0,0));
}

vec3 model_position()
{
    return transform_point(MODEL, vec3(0,0,0));
}

vec2 screen_uv()
{
    #ifdef PIXEL_SHADER
    {
        return vec2(gl_FragCoord) / vec2(RESOLUTION);
    }
    #else
    {
        return project_point(PROJECTION * CAMERA, POSITION).xy * 0.5 + 0.5;
    }
    #endif //PIXEL_SHADER
}

ivec2 screen_pixel()
{
    #ifdef PIXEL_SHADER
    {
        return ivec2(floor(gl_FragCoord.xy));
    }
    #else
    {
        return ivec2(floor(screen_uv() * RESOLUTION));
    }
    #endif
}

vec3 screen_to_camera(vec2 uv, float depth)
{
    vec3 clip_position = vec3(uv, depth) * 2.0 - 1.0;
    vec4 camera_position = inverse(PROJECTION) * vec4(clip_position, 1.0);
    camera_position /= camera_position.w;

    return camera_position.xyz;
}

vec3 view_direction()
{
    return transform_normal(inverse(CAMERA), screen_to_camera(screen_uv(), 1));
}

float pixel_depth()
{
    #ifdef PIXEL_SHADER
    {
        return gl_FragCoord.z;
    }
    #endif

    return 0.0;
}

float depth_to_z(float depth)
{
    return screen_to_camera(vec2(0,0), depth).z;
}

float pixel_world_size_at(float depth)
{
    vec2 uv = screen_uv();
    vec2 offset = vec2(1.0 / RESOLUTION.x, 0);
    return distance(screen_to_camera(uv, depth), screen_to_camera(uv + offset, depth));
}

float pixel_world_size()
{
    #ifdef PIXEL_SHADER
    {
        return pixel_world_size_at(gl_FragCoord.z);
    }
    #else
    {
        return pixel_world_size_at(project_point(PROJECTION * CAMERA, POSITION).z * 0.5 + 0.5);
    }
    #endif
}

vec3 _reconstruct_cs_position(sampler2D depth_texture, int depth_channel, ivec2 texel)
{
    float depth = texelFetch(depth_texture, texel, 0)[depth_channel];
    ivec2 size = textureSize(depth_texture, 0);
    vec2 uv = (vec2(texel) + vec2(0.5)) / vec2(size);

    return screen_to_camera(uv, depth);
}

vec3 reconstruct_normal(sampler2D depth_texture, int depth_channel, ivec2 texel)
{
    vec3 t0 = _reconstruct_cs_position(depth_texture, depth_channel, texel);
    vec3 x1 = _reconstruct_cs_position(depth_texture, depth_channel, texel + ivec2(-1, 0));
    vec3 x2 = _reconstruct_cs_position(depth_texture, depth_channel, texel + ivec2( 1, 0));
    vec3 y1 = _reconstruct_cs_position(depth_texture, depth_channel, texel + ivec2( 0,-1));
    vec3 y2 = _reconstruct_cs_position(depth_texture, depth_channel, texel + ivec2( 0, 1));

    vec3 x = distance(x1.z, t0.z) < distance(x2.z, t0.z) ? x1 : x2;
    vec3 y = distance(y1.z, t0.z) < distance(y2.z, t0.z) ? y1 : y2;

    vec3 n = normalize(cross(x - t0, y - t0));
    n = dot(n, t0) < 0 ? n : -n;

    return transform_normal(inverse(CAMERA), n);
}

/*  META
    @ray_origin: subtype=Vector;
    @ray_direction: subtype=Vector;
    @plane_position: subtype=Vector;
    @plane_normal: subtype=Normal;
*/
float ray_plane_intersection(vec3 ray_origin, vec3 ray_direction, vec3 plane_position, vec3 plane_normal)
{
    float r_direction = dot(ray_direction, plane_normal);
    float r_origin = dot(ray_origin, plane_normal);
    float p_position = dot(plane_position, plane_normal);

    return (p_position - r_origin) / r_direction;
}

vec2 rotate_2d(vec2 p, float angle)
{
    float c = cos(angle);
    float s = sin(angle);

    return vec2
    (
        p.x * c - p.y * s, 
        p.x * s + p.y * c
    );
}

#endif //COMMON_TRANSFORM_GLSL

