//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#include "NPR_Pipeline.glsl"

uniform sampler2D matcap_texture;

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    PO.color = get_matcap(matcap_texture);
}

