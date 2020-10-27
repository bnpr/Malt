//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform vec3 diffuse_color = vec3(1.0,0.1,0.1);
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float roughness = 0.5;

uniform sampler2D normal_map;
uniform int uv_index = 0;

@PRE_PASS_PIXEL_SHADER
{
    DEFAULT_PRE_PASS_PIXEL_SHADER();

    OUT_NORMAL_DEPTH.xyz = sample_normal_map(normal_map, uv_index);
}

@MAIN_PASS_PIXEL_SHADER
{
    vec3 diffuse = diffuse_color * get_diffuse_half();
    vec3 specular = specular_color * get_specular(roughness);
    vec3 color = ambient_color + diffuse + specular;

    OUT_COLOR = vec4(color, 1.0);
}

