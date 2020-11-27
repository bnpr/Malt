//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Pipelines/NPR_Pipeline.glsl"

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform vec4 diffuse_color = vec4(1.0,0.1,0.1,0.5);
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float roughness = 0.5;

uniform sampler2D alpha_texture;

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec3 diffuse = diffuse_color.rgb * get_diffuse_half();
    vec3 specular = specular_color * get_specular(roughness);

    vec3 color = ambient_color + diffuse + specular;
    float alpha = diffuse_color.a + luma(specular);
    alpha = clamp(alpha, 0, 1);

    PO.color.rgb = color;
    PO.color.a = alpha;
    PO.shadow_color = diffuse_color;
}

