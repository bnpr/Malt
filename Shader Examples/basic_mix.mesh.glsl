//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "NPR_Pipeline.glsl"

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform vec3 diffuse_color = vec3(1.0,0.1,0.1);
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float roughness = 0.5;

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec3 color = ambient_color;
    color = mix(color, diffuse_color, get_diffuse_half());
    color = mix(color, specular_color, get_specular(roughness));

    PO.color = vec4(color, 1.0);
}

