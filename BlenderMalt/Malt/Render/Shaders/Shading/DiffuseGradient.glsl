//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef SHADING_DIFFUSE_GRADIENT_GLSL
#define SHADING_DIFFUSE_GRADIENT_GLSL

#include "Common/Lighting.glsl"

vec3 diffuse_gradient_light(LitSurface surface, sampler1D gradient)
{
    return texture(gradient, ((surface.NoL + 1.0) / 2.0)).rgb * surface.P;
}

vec3 diffuse_gradient_bsdf(vec3 position, vec3 normal, sampler1D gradient)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * diffuse_gradient_light(surface, gradient);
    }

    return result;
}

#endif SHADING_DIFFUSE_GRADIENT_GLSL

