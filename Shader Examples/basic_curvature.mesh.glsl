//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

uniform sampler1D ramp;

@MAIN_PASS_PIXEL_SHADER
{
    //float curvature = get_curvature();
    float curvature = get_surface_curvature(0.5);

    OUT_COLOR = texture(ramp, curvature);
}

