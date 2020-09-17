//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

uniform float angle = 360;

uniform float angle_smooth_start = 1.0;
uniform float angle_smooth_end = -1.0;

uniform float facing_smooth_start = 0.6;
uniform float facing_smooth_end = 0.55;

@MAIN_PASS_PIXEL_SHADER
{
    float rim = get_rim_light(angle, angle_smooth_start, angle_smooth_end, facing_smooth_start, facing_smooth_end);

    OUT_COLOR = vec4(rim);
    OUT_COLOR.a = 1.0;
}

