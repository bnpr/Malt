//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Common.glsl"

#ifdef VERTEX_SHADER
void DEFAULT_COMMON_VERTEX_SHADER()
{
    DEFAULT_VERTEX_SHADER();
}
#endif

#ifdef PIXEL_SHADER

uniform float ID;

#ifdef PRE_PASS
layout (location = 0) out vec4 OUT_NORMAL_DEPTH;
layout (location = 1) out float OUT_ID;

void DEFAULT_PRE_PASS_PIXEL_SHADER()
{
    OUT_NORMAL_DEPTH.xyz = normalize(NORMAL);
    if(!gl_FrontFacing)
    {
        OUT_NORMAL_DEPTH.xyz *= -1.0;
    }
    OUT_NORMAL_DEPTH.w = gl_FragCoord.z;
    OUT_ID = ID;
}
#endif //PRE_PASS

#ifdef MAIN_PASS
uniform sampler2D IN_NORMAL_DEPTH;
uniform sampler2D IN_ID;

layout (location = 0) out vec4 OUT_COLOR;
layout (location = 1) out vec4 OUT_LINE_COLOR;
layout (location = 2) out vec4 OUT_LINE_DATA;

void DEFAULT_MAIN_PASS_PIXEL_SHADER()
{
    OUT_COLOR = vec4(1.0,1.0,0.0,1.0);
}
#endif //MAIN_PASS

#endif //PIXEL_SHADER

//NPR PIPELINE SIMPLIFIED API

#ifdef PIXEL_SHADER

#ifdef MAIN_PASS

#include "Shading/Lambert.glsl"
#include "Shading/Phong.glsl"
#include "Shading/DiffuseGradient.glsl"
#include "Shading/Rim.glsl"
#include "Shading/SpecularGradient.glsl"
#include "Filters/Curvature.glsl"
#include "Filters/Line.glsl"

vec3 get_normal()
{
    //TODO: This returns lower quality normals than NORMAL
    return texture(IN_NORMAL_DEPTH, screen_uv()).xyz;
}

vec3 get_diffuse()
{
    return lambert_bsdf(POSITION, get_normal());
}

vec3 get_diffuse_half()
{
    return half_lambert_bsdf(POSITION, get_normal());
}

vec3 get_specular(float shininess)
{
    return phong_bsdf(POSITION, get_normal(), shininess);
}

vec3 get_diffuse_gradient(sampler1D gradient_texture)
{
    return diffuse_gradient_bsdf(POSITION, get_normal(), gradient_texture);
}

vec3 get_specular_gradient(sampler1D gradient_texture, float shininess)
{
    return specular_gradient_bsdf(POSITION, get_normal(), shininess, gradient_texture);
}

float get_curvature()
{
    vec3 x = transform_normal(inverse(CAMERA), vec3(1,0,0));
    vec3 y = transform_normal(inverse(CAMERA), vec3(0,1,0));
    return curvature(IN_NORMAL_DEPTH, screen_uv(), 1.0, x, y);
}

float get_surface_curvature(float depth_range /*0.05*/)
{
    vec3 x = transform_normal(inverse(CAMERA), vec3(1,0,0));
    vec3 y = transform_normal(inverse(CAMERA), vec3(0,1,0));
    return surface_curvature(IN_NORMAL_DEPTH, IN_NORMAL_DEPTH, 3, screen_uv(), 1.0, x, y, depth_range);
}

float get_facing()
{
    float d = dot(get_normal(), view_direction());
    return clamp(d, 0.0, 1.0);
}

float get_fresnel()
{
    return 1.0 - get_facing();
}

vec4 get_matcap(sampler2D matcap_texture)
{
    return texture(matcap_texture, matcap_uv(get_normal()));
}

float get_rim_light(float angle, float angle_smooth_start, float angle_smooth_end, float facing_smooth_start, float facing_smooth_end)
{
    return rim_light(get_normal(), angle * DEGREES_TO_RADIANS, angle_smooth_start, angle_smooth_end, facing_smooth_start, facing_smooth_end);
}

//TODO: World Space width for curvature

float get_line_simple(float width, float depth_threshold, float normal_threshold)
{
    LineOutput lo = line_ex(
        width,
        1,
        LINE_DEPTH_MODE_NEAR,
        screen_uv(),
        IN_NORMAL_DEPTH,
        3,
        IN_NORMAL_DEPTH,
        IN_ID,
        0
    );

    bool line = lo.id_boundary || 
                lo.delta_distance > depth_threshold ||
                lo.delta_angle > normal_threshold;
    
    return float(line);
}

float get_line_advanced(
    float id_boundary_width,
    float min_depth_threshold, float max_depth_threshold, float min_depth_width, float max_depth_width,
    float min_angle_threshold, float max_angle_threshold, float min_angle_width, float max_angle_width
)
{
    LineOutput lo = line_ex(
        1.0,
        1,
        LINE_DEPTH_MODE_NEAR,
        screen_uv(),
        IN_NORMAL_DEPTH,
        3,
        IN_NORMAL_DEPTH,
        IN_ID,
        0
    );

    float line = lo.id_boundary ? id_boundary_width : 0.0;
    
    if(lo.delta_distance > min_depth_threshold)
    {
        float depth = map_range_clamped(
            lo.delta_distance, 
            min_depth_threshold, max_depth_threshold,
            min_depth_width, max_depth_width
        );

        line = max(line, depth);
    }
    if(lo.delta_angle > min_angle_threshold)
    {
        float angle = map_range_clamped(
            lo.delta_angle, 
            min_angle_threshold, max_angle_threshold,
            min_angle_width, max_angle_width
        );

        line = max(line, angle);
    }

    return line;
}

#endif //MAIN_PASS

#endif //PIXEL_SHADER

