//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform sampler2D diffuse_texture;
uniform int uv_index = 0;
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float roughness = 0.5;

@MAIN_PASS_PIXEL_SHADER
{
    vec3 diffuse_color = texture(diffuse_texture, UV[uv_index]).rgb;
    vec3 diffuse = diffuse_color * get_diffuse_half();
    vec3 specular = specular_color * get_specular(roughness);
    vec3 color = ambient_color + diffuse + specular;

    OUT_COLOR = vec4(color, 1.0);
}

