//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef SHADING_PHONG_GLSL
#define SHADING_PHONG_GLSL

#include "Common/Lighting.glsl"

float phong_light(LitSurface surface, float shininess)
{
    float NoH = dot(surface.V, surface.R);
    NoH *= 1.0 - pow(1.0 - clamp(surface.NoL, 0, 1), 20.0);
    NoH = clamp(NoH, 0, 1);
    return pow(NoH, shininess) * surface.P;
    
    return 0.0;
}

vec3 phong_bsdf(vec3 position, vec3 normal, float shininess)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * phong_light(surface, shininess);
    }

    return result;
}

#endif //SHADING_PHONG_GLSL

