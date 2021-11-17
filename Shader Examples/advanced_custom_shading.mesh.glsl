//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#include "NPR_Pipeline.glsl"
#include "Shading/ShadingModels.glsl"

uniform vec3 ao_color = vec3(0.0);
uniform float ao_radius = 0.75;
uniform int ao_samples = 16;
uniform vec3 ambient_color = vec3(0.15);
uniform vec3 color = vec3(0.5);
uniform float roughness = 0.5;
uniform float metalness = 0.0;

vec3 BRDF(LitSurface LS, float ao)
{
    float NoL = LS.NoL;
    NoL = max(MIN_DOT, NoL);

    float NoV = dot(LS.N, LS.V);
    NoV = max(MIN_DOT, NoV);

    float NoH = dot(LS.N, LS.H);
    NoH = max(MIN_DOT, NoH);

    float LoV = dot(LS.L, LS.V);
    LoV = max(MIN_DOT, LoV);

    float VoH = dot(LS.V, LS.H);
    VoH = max(MIN_DOT, VoH);

    float a = max(0.001, roughness * roughness);

    //Diffuse Models
    float burley = BRDF_burley(NoL, NoV, VoH, a);
    float oren_nayar = BRDF_oren_nayar(NoL, NoV, LoV, a);
    float lambert = BRDF_lambert(NoL);

    //Specular Distribution Models
    float d_phong = D_blinn_phong(NoH, a);
    float d_beckmann = D_beckmann(NoH, a);
    float d_ggx = D_GGX(NoH, a);

    //Specular Geometric Shadowing Models
    float g_cook_torrance = G_cook_torrance(NoH, NoV, NoL, VoH);
    float g_beckmann = G_beckmann(NoL, NoV, a);
    float g_ggx = G_GGX(NoL, NoV, a);

    float dielectric = 0.04;
    float F0 = mix(dielectric, 1.0, metalness);
    //Specular Fresnel Models
    float f_schlick = F_schlick(VoH, F0, 1.0);
    float f_cook_torrance = F_cook_torrance(VoH, F0);

    
    // Disney-like PBR shader (Burley for diffuse + GGX for speculars)
    vec3 shadow_color = ambient_color * mix(ao_color, vec3(1.0), ao);
    
    vec3 diffuse_color = color * burley * (1.0 - f_schlick) * (1.0 - metalness);
    
    float specular = BRDF_specular_cook_torrance(d_ggx, f_schlick, g_ggx, NoL, NoV);
    vec3 specular_color = mix(vec3(specular), color * specular, metalness);

    vec3 lit_color = diffuse_color + specular_color;

    return mix(shadow_color, lit_color, LS.light_color * LS.shadow_multiply * NoL);
}

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec3 result = vec3(0,0,0);

    float ao = get_ao(ao_samples, ao_radius);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light L = LIGHTS.lights[i];
        LitSurface LS = NPR_lit_surface(S.position, S.normal, S.id, L, i, Settings.Receive_Shadow, Settings.Self_Shadow);

        result += BRDF(LS, ao);
    }

    PO.color.rgb = result;
}

