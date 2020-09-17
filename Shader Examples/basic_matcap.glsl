//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

uniform sampler2D matcap_texture;

@MAIN_PASS_PIXEL_SHADER
{
    OUT_COLOR = get_matcap(matcap_texture);
}

