//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Pipelines/NPR_Pipeline.glsl"

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform vec3 diffuse_color = vec3(1.0,0.1,0.1);
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float roughness = 0.5;

uniform int uv_index = 0;
uniform sampler2D main_normal_map;
uniform sampler2D detail_normal_map;
uniform float detail_uv_scale = 1.0;
uniform float detail_blend_factor = 0.5;

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec3 diffuse = diffuse_color * get_diffuse_half();
    vec3 specular = specular_color * get_specular(roughness);
    vec3 color = ambient_color + diffuse + specular;

    PO.color = vec4(color, 1.0);
    
    vec3 main_normal = sample_normal_map(main_normal_map, uv_index);
    vec3 detail_normal = sample_normal_map_ex(detail_normal_map, uv_index, S.uv[uv_index] * detail_uv_scale);

    vec3 main_gradient = surface_gradient_from_normal(main_normal);
    vec3 detail_gradient = surface_gradient_from_normal(detail_normal);

    PO.normal = normal_from_surface_gradient(main_gradient + detail_gradient * detail_blend_factor);
}

