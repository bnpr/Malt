//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef SHADING_SPECULAR_GRADIENT_GLSL
#define SHADING_SPECULAR_GRADIENT_GLSL

#include "Common/Lighting.glsl"
#include "Shading/Phong.glsl"

vec3 specular_gradient_light(LitSurface surface, float roughness, sampler1D gradient)
{
    return texture(gradient, phong_light(surface, roughness)).rgb;
}

vec3 specular_gradient_bsdf(vec3 position, vec3 normal, float roughness, sampler1D gradient)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * specular_gradient_light(surface, roughness, gradient);
    }

    return result;
}

#endif //SHADING_SPECULAR_GRADIENT_GLSL

