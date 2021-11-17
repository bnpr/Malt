//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#define CUSTOM_VERTEX_DISPLACEMENT

#include "NPR_Pipeline.glsl"

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform vec3 diffuse_color = vec3(1.0,0.1,0.1);
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float roughness = 0.5;

uniform float wave_frequency = 4.0;
uniform float wave_size = 0.2;
uniform float wave_time_scale = 1.0;

vec3 VERTEX_DISPLACEMENT_SHADER(Surface S)
{
    vec3 displacement = vec3(0);
    displacement.z = sin(S.position.x * wave_frequency + TIME * wave_time_scale) * wave_size;
    return displacement;
}

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec3 diffuse = diffuse_color * get_diffuse_half();
    vec3 specular = specular_color * get_specular(roughness);
    vec3 color = ambient_color + diffuse + specular;

    PO.color.rgb = color;
}

