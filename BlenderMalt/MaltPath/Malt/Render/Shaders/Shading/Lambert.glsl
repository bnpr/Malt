//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef SHADING_LAMBERT_GLSL
#define SHADING_LAMBERT_GLSL

#include "Common/Lighting.glsl"

float lambert_light(LitSurface surface)
{
    return surface.shadow ? 0 : clamp(surface.NoL, 0, 1) * surface.P;
}

float half_lambert_light(LitSurface surface)
{
    return min(surface.shadow ? 0.5 : 1.0 ,((surface.NoL + 1.0) / 2.0)) * surface.P;
}

vec3 lambert_bsdf(vec3 position, vec3 normal)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * lambert_light(surface);
    }

    return result;
}

vec3 half_lambert_bsdf(vec3 position, vec3 normal)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * half_lambert_light(surface);
    }

    return result;
}

#endif //SHADING_LAMBERT_GLSL

