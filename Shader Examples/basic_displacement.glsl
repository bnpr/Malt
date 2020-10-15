//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform vec3 diffuse_color = vec3(1.0,0.1,0.1);
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float roughness = 0.5;

uniform float wave_frequency = 4.0;
uniform float wave_size = 0.2;
uniform float wave_time_scale = 1.0;

uniform float displacement_calculation_offset = 0.01;

vec3 displace(vec3 position)
{
    position.z += sin(position.x * wave_frequency + TIME * wave_time_scale) * wave_size;
    return position;
}

@COMMON_VERTEX_SHADER
{
    DEFAULT_VERTEX_SHADER();

    VERTEX_DISPLACEMENT(displace, displacement_calculation_offset);

    VERTEX_SETUP_OUTPUT();
}

@MAIN_PASS_PIXEL_SHADER
{
    vec3 diffuse = diffuse_color * get_diffuse_half();
    vec3 specular = specular_color * get_specular(roughness);
    vec3 color = ambient_color + diffuse + specular;

    OUT_COLOR = vec4(color, 1.0);
}

