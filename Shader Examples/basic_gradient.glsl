//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

uniform sampler1D diffuse_gradient;
uniform sampler1D specular_gradient;
uniform float shininess = 32;

@MAIN_PASS_PIXEL_SHADER
{
    vec3 color = get_diffuse_gradient(diffuse_gradient);
    color += get_specular_gradient(specular_gradient, shininess);

    OUT_COLOR = vec4(color, 1.0);
}

