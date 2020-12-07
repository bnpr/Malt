//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Pipelines/NPR_Pipeline.glsl"

uniform sampler1D ramp;

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    //float curvature = get_curvature();
    float curvature = get_surface_curvature(0.5);

    PO.color = texture(ramp, curvature);
}

