//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef SHADING_RIM_GLSL
#define SHADING_RIM_GLSL

float rim_light(vec3 normal, float angle, float angle_smooth_start, float angle_smooth_end, float facing_smooth_start, float facing_smooth_end)
{
    vec2 angle_vec = vec2(cos(angle), sin(angle));

    vec3 r = cross(transform_normal(CAMERA, view_direction()), transform_normal(CAMERA, normal));
    vec2 r2d = normalize(r.xy);

    float angle_dot = dot(r2d, angle_vec);
    angle_dot = angle_dot * 0.5 + 0.5;
    float facing_dot = dot(view_direction(), normal);
    facing_dot = 1.0 - facing_dot;

    float angle_result = map_range_clamped(angle_dot, angle_smooth_end, angle_smooth_start, 0.0, 1.0);
    float facing_result = map_range_clamped(facing_dot * angle_result, facing_smooth_end, facing_smooth_start, 0.0, 1.0);

    return angle_result * facing_result;
}

#endif //SHADING_RIM_GLSL

