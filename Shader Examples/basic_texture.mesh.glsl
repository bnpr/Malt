//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Pipelines/NPR_Pipeline.glsl"

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform sampler2D diffuse_texture;
uniform int uv_index = 0;
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float roughness = 0.5;

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec3 diffuse_color = texture(diffuse_texture, UV[uv_index]).rgb;
    vec3 diffuse = diffuse_color * get_diffuse();
    vec3 specular = specular_color * get_specular(roughness);
    vec3 color = ambient_color + diffuse + specular;

    PO.color = vec4(diffuse_color, 1.0);
}

