//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef NPR_SHADING_GLSL
#define NPR_SHADING_GLSL

#include "NPR_Lighting.glsl"
#include "Shading/ShadingModels.glsl"

vec3 lit_diffuse(LitSurface LS)
{
    return clamp(LS.NoL, 0, 1) * LS.light_color * LS.shadow_multiply;
}

vec3 _lit_diffuse_half_common(LitSurface LS)
{
    vec3 diffuse = vec3(map_range_clamped(LS.NoL, -1, 1, 0, 1));
    vec3 shadow = map_range_clamped(LS.shadow_multiply, vec3(0),vec3(1),vec3(0.5),vec3(1));
    return min(diffuse, shadow);
}

vec3 lit_diffuse_half(LitSurface LS)
{
    return _lit_diffuse_half_common(LS) * LS.light_color;
}

vec3 lit_diffuse_gradient(LitSurface LS, sampler1D gradient)
{
    return rgb_gradient(gradient, _lit_diffuse_half_common(LS)) * LS.light_color;
}

float _specular_shadowing(float NoL, float specular)
{
    return clamp(specular * (1.0 - pow(1.0 - max(NoL, 0), 20.0)), 0, 1);
}

float _lit_specular_common(LitSurface LS, float roughness)
{
    float VoR = dot(LS.V, LS.R);
    VoR = _specular_shadowing(LS.NoL, VoR);
    return pow(VoR, roughness_to_shininess(roughness));
}

vec3 lit_specular(LitSurface LS, float roughness)
{
    return _lit_specular_common(LS, roughness) * LS.light_color * LS.shadow_multiply;
}

vec3 lit_specular_gradient(LitSurface LS, float roughness, sampler1D gradient)
{
    return texture(gradient, _lit_specular_common(LS, roughness)).rgb * LS.light_color * LS.shadow_multiply;
}

float _lit_specular_anisotropic_common(LitSurface LS, vec3 tangent, float anisotropy, float roughness)
{
    vec2 a = vec2(anisotropy, 1.0 - anisotropy);
    a *= roughness;
    vec3 bitangent = normalize(cross(LS.N, tangent));

    float NoL = max(dot(LS.N, LS.L), MIN_DOT);
    float NoV = max(dot(LS.N, LS.V), MIN_DOT);
    float NoH = max(dot(LS.H, LS.N), MIN_DOT);
    float XoH = dot(LS.H, tangent);
    float YoH = dot(LS.H, bitangent);

    float specular = D_ward(NoL, NoV, XoH, XoH, YoH, a.x, a.y);

    return _specular_shadowing(NoL, specular);
}

vec3 lit_specular_anisotropic(LitSurface LS, vec3 tangent, float anisotropy, float roughness)
{
    return _lit_specular_anisotropic_common(LS, tangent, anisotropy, roughness) * LS.light_color * LS.shadow_multiply;
}

vec3 lit_specular_anisotropic_gradient(LitSurface LS, vec3 tangent, float anisotropy, float roughness, sampler1D gradient)
{
    return texture(gradient, _lit_specular_anisotropic_common(LS, tangent, anisotropy, roughness)).rgb * LS.light_color * LS.shadow_multiply;
}

vec3 lit_toon(LitSurface LS, float size, float gradient_size, float specularity, float offset)
{
    float D = mix(LS.NoL, dot(LS.V, LS.R), specularity);

    float angle = acos(D);
    float delta = angle / PI;
    delta -= offset;

    gradient_size = min(size, gradient_size);

    float value = 1.0 - map_range_clamped(delta, size - gradient_size, size, 0.0, 1.0);

    float color_at_05 =  1.0 - map_range_clamped(0.5, size - gradient_size, size, 0.0, 1.0);

    return min(LS.shadow ? color_at_05 : 1.0, value) * LS.light_color;
}

#define _LIT_SCENE_MACRO(callback)\
    vec3 result = vec3(0,0,0);\
    for (int i = 0; i < LIGHTS.lights_count; i++)\
    {\
        Light L = LIGHTS.lights[i];\
        LitSurface LS = NPR_lit_surface(position, normal, ID, L, i);\
        result += (callback);\
    }\
    return result;\

vec3 scene_diffuse(vec3 position, vec3 normal) 
{ 
    _LIT_SCENE_MACRO(lit_diffuse(LS));
}

vec3 scene_diffuse_half(vec3 position, vec3 normal) 
{ 
    _LIT_SCENE_MACRO(lit_diffuse_half(LS));
}

vec3 scene_diffuse_gradient(vec3 position, vec3 normal, sampler1D gradient)
{
    _LIT_SCENE_MACRO(lit_diffuse_gradient(LS, gradient));
}

vec3 scene_specular(vec3 position, vec3 normal, float roughness) 
{
    _LIT_SCENE_MACRO(lit_specular(LS, roughness));
}

vec3 scene_specular_gradient(vec3 position, vec3 normal, float roughness, sampler1D gradient)
{
    _LIT_SCENE_MACRO(lit_specular_gradient(LS, roughness, gradient));
}

vec3 scene_specular_anisotropic(vec3 position, vec3 normal, vec3 tangent, float anisotropy, float roughness)
{
    _LIT_SCENE_MACRO(lit_specular_anisotropic(LS, tangent, anisotropy, roughness));
}

vec3 scene_specular_anisotropic_gradient(vec3 position, vec3 normal, vec3 tangent, float anisotropy, float roughness, sampler1D gradient)
{
    _LIT_SCENE_MACRO(lit_specular_anisotropic_gradient(LS, tangent, anisotropy, roughness, gradient));
}

vec3 scene_toon(vec3 position, vec3 normal, float size, float gradient_size, float specularity, float offset)
{
    _LIT_SCENE_MACRO(lit_toon(LS, size, gradient_size, specularity, offset));
}

#endif //NPR_SHADING_GLSL

