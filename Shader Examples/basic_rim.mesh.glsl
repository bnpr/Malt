//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#include "NPR_Pipeline.glsl"

uniform float rim_angle = 360;

uniform float rim_length = 2.0;
uniform float rim_thickness = 0.4;
uniform float rim_thickness_falloff = 0.1;


void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    float rim = get_rim_light(rim_angle, rim_length, rim_thickness, rim_thickness_falloff);

    PO.color = vec4(rim);
    PO.color.a = 1.0;
}

