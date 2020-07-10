//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef SHADING_SPECULAR_GRADIENT_GLSL
#define SHADING_SPECULAR_GRADIENT_GLSL

#include "Common/Lighting.glsl"

vec3 specular_gradient_light(LitSurface surface, float shininess, sampler1D gradient)
{
    float NoH = dot(surface.V, surface.R);
    NoH *= 1.0 - pow(1.0 - clamp(surface.NoL, 0, 1), 20.0);
    NoH = clamp(NoH, 0, 1);

    return texture(gradient, pow(NoH, shininess)).rgb * surface.P;
}

vec3 specular_gradient_bsdf(vec3 position, vec3 normal, float shininess, sampler1D gradient)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * specular_gradient_light(surface, shininess, gradient);
    }

    return result;
}

#endif SHADING_SPECULAR_GRADIENT_GLSL

