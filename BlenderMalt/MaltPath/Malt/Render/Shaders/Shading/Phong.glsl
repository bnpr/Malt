//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef SHADING_PHONG_GLSL
#define SHADING_PHONG_GLSL

#include "Common/Lighting.glsl"
#include "Shading/ShadingModels.glsl"

float phong_light(LitSurface surface, float roughness)
{
    float VoR = dot(surface.V, surface.R);
    VoR *= 1.0 - pow(1.0 - clamp(surface.NoL, 0, 1), 20.0);
    VoR = clamp(VoR, 0, 1);
    
    return surface.shadow ? 0 : pow(VoR, roughness_to_shininess(roughness)) * surface.P;
}

vec3 phong_bsdf(vec3 position, vec3 normal, float roughness)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * phong_light(surface, roughness);
    }

    return result;
}

#endif //SHADING_PHONG_GLSL

