//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#include "NPR_Pipeline.glsl"

uniform sampler1D diffuse_gradient;
uniform sampler1D specular_gradient;
uniform float roughness = 0.5;

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec3 color = get_diffuse_gradient(diffuse_gradient);
    color += get_specular_gradient(specular_gradient, roughness);

    PO.color.rgb = color;
}

