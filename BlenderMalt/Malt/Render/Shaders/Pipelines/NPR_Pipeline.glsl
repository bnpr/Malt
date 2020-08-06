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
    OUT_NORMAL_DEPTH.rgb = normalize(NORMAL);
    OUT_NORMAL_DEPTH.a = gl_FragCoord.z;
    OUT_ID = ID;
}
#endif //PRE_PASS

#ifdef MAIN_PASS
uniform sampler2D IN_NORMAL_DEPTH;
uniform sampler2D IN_ID;

layout (location = 0) out vec4 OUT_COLOR;

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
#include "Shading/SpecularGradient.glsl"
#include "Filters/Line.glsl"

vec3 get_normal()
{
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

#endif //MAIN_PASS

#endif //PIXEL_SHADER

