//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef SHADING_NPR_GLSL
#define SHADING_NPR_GLSL

#include "Common/Lighting.glsl"
#include "Shading/ShadingModels.glsl"

float _specular_shadowing(float NoL, float specular)
{
    return clamp(specular * (1.0 - pow(1.0 - max(NoL, 0), 20.0)), 0, 1);
}

float diffuse_light(LitSurface surface)
{
    return surface.shadow ? 0 : clamp(surface.NoL, 0, 1) * surface.P;
}

float half_diffuse_light(LitSurface surface)
{
    return min(surface.shadow ? 0.5 : 1.0 ,((surface.NoL + 1.0) / 2.0)) * surface.P;
}

float specular_light(LitSurface surface, float roughness)
{
    float VoR = dot(surface.V, surface.R);
    VoR = _specular_shadowing(surface.NoL, VoR);
    
    return surface.shadow ? 0 : pow(VoR, roughness_to_shininess(roughness)) * surface.P;
}

float specular_anisotropic_light(LitSurface surface, vec3 tangent, float anisotropy, float roughness)
{
    vec2 a = vec2(anisotropy, 1.0 - anisotropy);
    a *= roughness;
    vec3 bitangent = normalize(cross(surface.N, tangent));

    float NoL = max(dot(surface.N, surface.L), MIN_DOT);
    float NoV = max(dot(surface.N, surface.V), MIN_DOT);
    float NoH = max(dot(surface.H, surface.N), MIN_DOT);
    float XoH = dot(surface.H, tangent);
    float YoH = dot(surface.H, bitangent);

    float specular = D_ward(NoL, NoV, XoH, XoH, YoH, a.x, a.y);

    return surface.shadow ? 0 : _specular_shadowing(NoL, specular) * surface.P;
}

float toon_light(LitSurface surface, float size, float gradient_size, float specularity, float offset)
{
    float D = mix(surface.NoL, dot(surface.V, surface.R), specularity);

    float angle = acos(D);
    float delta = angle / PI;
    delta -= offset;

    gradient_size = min(size, gradient_size);

    float value = 1.0 - map_range_clamped(delta, size - gradient_size, size, 0.0, 1.0);

    float color_at_05 =  1.0 - map_range_clamped(0.5, size - gradient_size, size, 0.0, 1.0);

    return min(surface.shadow ? color_at_05 : 1.0, value) * surface.P;
}

vec3 scene_diffuse(vec3 position, vec3 normal)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * diffuse_light(surface);
    }

    return result;
}

vec3 scene_half_diffuse(vec3 position, vec3 normal)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * half_diffuse_light(surface);
    }

    return result;
}

vec3 scene_diffuse_gradient(vec3 position, vec3 normal, sampler1D gradient)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * texture(gradient, half_diffuse_light(surface)).rgb;
    }

    return result;
}

vec3 scene_specular(vec3 position, vec3 normal, float roughness)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * specular_light(surface, roughness);
    }

    return result;
}

vec3 scene_specular_gradient(vec3 position, vec3 normal, float roughness, sampler1D gradient)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * texture(gradient, specular_light(surface, roughness)).rgb;
    }

    return result;
}

vec3 scene_specular_anisotropic(vec3 position, vec3 normal, vec3 tangent, float anisotropy, float roughness)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * specular_anisotropic_light(surface, tangent, anisotropy, roughness);
    }

    return result;
}

vec3 scene_specular_anisotropic_gradient(vec3 position, vec3 normal, vec3 tangent, float anisotropy, float roughness, sampler1D gradient)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * texture(gradient, specular_anisotropic_light(surface, tangent, anisotropy, roughness)).rgb;
    }

    return result;
}

vec3 scene_toon(vec3 position, vec3 normal, float size, float gradient_size, float specularity, float offset)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * toon_light(surface, size, gradient_size, specularity, offset);
    }

    return result;
}

vec3 scene_toon_gradient(vec3 position, vec3 normal, float size, float gradient_size, float specularity, float offset, sampler1D gradient)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(position, normal, light);
        result += light.color * texture(gradient, toon_light(surface, size, gradient_size, specularity, offset)).rgb;
    }

    return result;
}

#endif //SHADING_NPR_GLSL

