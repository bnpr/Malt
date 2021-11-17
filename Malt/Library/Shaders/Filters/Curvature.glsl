//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#ifndef CURVATURE_GLSL
#define CURVATURE_GLSL

#include "Common/Math.glsl"

// x and y must be the screen x and y axis in the same coordinate space as the texture normals
float curvature(sampler2D normal_texture, vec2 uv, float width, vec3 x, vec3 y)
{
    vec2 offset = vec2(width) / vec2(textureSize(normal_texture, 0));

    vec3 l = texture(normal_texture, uv + vec2(-offset.x,0)).xyz;
    vec3 r = texture(normal_texture, uv + vec2( offset.x,0)).xyz;
    vec3 d = texture(normal_texture, uv + vec2(0,-offset.y)).xyz;
    vec3 u = texture(normal_texture, uv + vec2(0, offset.y)).xyz;

    if(width != 1.0)
    {
        l = normalize(l);
        r = normalize(r);
        d = normalize(d);
        u = normalize(u);
    }

    float curvature = (dot(u,y) - dot(d,y)) + (dot(r,x) - dot(l,x));

    return map_range_clamped(curvature, -1, 1, 0, 1);
}

#include "Filters/Line.glsl"

// Like curvature, but discard depth discontinuities
float surface_curvature(sampler2D normal_texture, sampler2D depth_texture, int depth_channel, 
    vec2 uv, float width, vec3 x, vec3 y, float depth_range)
{
    float curvature = curvature(normal_texture, uv, width, x, y);

    float delta_depth = line_detection_depth(depth_texture, depth_channel, uv, width, LINE_DEPTH_MODE_ANY);

    delta_depth /= depth_range;
    delta_depth = clamp(delta_depth, 0, 1);

    return mix(curvature, 0.5, delta_depth);
}

#endif //CURVATURE_GLSL

