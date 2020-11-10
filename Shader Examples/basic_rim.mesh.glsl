//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

uniform float rim_angle = 360;

uniform float rim_length = 2.0;
uniform float rim_thickness = 0.4;
uniform float rim_thickness_falloff = 0.1;


@MAIN_PASS_PIXEL_SHADER
{
    float rim = get_rim_light(rim_angle, rim_length, rim_thickness, rim_thickness_falloff);

    OUT_COLOR = vec4(rim);
    OUT_COLOR.a = 1.0;
}

