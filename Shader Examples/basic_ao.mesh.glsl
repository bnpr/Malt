//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

uniform int ao_samples = 16;
uniform float ao_radius = 0.75;


@MAIN_PASS_PIXEL_SHADER
{
    float ao = get_ao(ao_samples, ao_radius);
    OUT_COLOR.rgb = vec3(ao);
    OUT_COLOR.a = 1.0;
}

