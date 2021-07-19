//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Pipelines/NPR_Pipeline.glsl"

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform vec3 diffuse_color = vec3(1.0,0.1,0.1);
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float roughness = 0.5;

uniform sampler2D normal_map;
uniform sampler2D secondary_normal_map;
uniform int uv_index = 0;

uniform float tiling_factor = 1.0;
uniform float blend_factor = 0.5;

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec3 diffuse = diffuse_color * get_diffuse_half();
    vec3 specular = specular_color * get_specular(roughness);
    vec3 color = ambient_color + diffuse + specular;

    vec3 perturbed_normal = sample_normal_map(normal_map, uv_index, tiling_factor);
    vec3 secondary_perturbed_normal = sample_normal_map(secondary_normal_map, uv_index, tiling_factor);

    vec3 s1 = surfgrad_from_perturbed_normal(perturbed_normal);
    vec3 s2 = surfgrad_from_perturbed_normal(secondary_perturbed_normal);

    vec3 normal = resolve_normal_from_surface_gradient(s1 + s2 * blend_factor);

    PO.color = vec4(color, 1.0);
    PO.normal = normal;
}

