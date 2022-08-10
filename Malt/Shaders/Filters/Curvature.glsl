#ifndef CURVATURE_GLSL
#define CURVATURE_GLSL

#include "Common/Math.glsl"

/*  META GLOBAL
    @meta: category=Filter;
*/

/*  META
    @meta: label=Normal Curvature;
    @uv: default=UV[0];
    @width: default=1.0;
    @x: subtype=Normal; default=vec3(1,0,0);
    @y: subtype=Normal; default=vec3(0,1,0);
*/
float curvature(sampler2D normal_texture, vec2 uv, float width, vec3 x, vec3 y)
{
    // x and y must be the screen x and y axis in the same coordinate space as the texture normals
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
/*  META
    @meta: internal=true;
    @uv: default=UV[0];
    @width: default=1.0;
    @x: subtype=Normal; default=vec3(1,0,0);
    @y: subtype=Normal; default=vec3(0,1,0);
    @depth_range: default=0.1;
*/
float surface_curvature(sampler2D normal_texture, sampler2D depth_texture, int depth_channel, 
    vec2 uv, float width, vec3 x, vec3 y, float depth_range)
{
    float curvature = curvature(normal_texture, uv, width, x, y);

    float delta_depth = _line_detection_depth(depth_texture, depth_channel, uv, width, LINE_DEPTH_MODE_ANY);

    delta_depth /= depth_range;
    delta_depth = clamp(delta_depth, 0, 1);

    return mix(curvature, 0.5, delta_depth);
}

#endif //CURVATURE_GLSL

