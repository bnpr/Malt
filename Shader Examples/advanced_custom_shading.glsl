//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Shading/ShadingModels.glsl"

uniform vec3 color = vec3(0.5);
uniform float roughness = 0.5;
uniform float metalness = 0.0;

vec3 BRDF(LitSurface S)
{
    if(S.shadow)
    {
        return vec3(0);
    }

    float NoL = S.NoL;
    NoL = max(MIN_DOT, NoL);

    float NoV = dot(S.N, S.V);
    NoV = max(MIN_DOT, NoV);

    float NoH = dot(S.N, S.H);
    NoH = max(MIN_DOT, NoH);

    float LoV = dot(S.L, S.V);
    LoV = max(MIN_DOT, LoV);

    float VoH = dot(S.V, S.H);
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
    vec3 diffuse_color = color * burley * (1.0 - f_schlick) * (1.0 - metalness);
    
    float specular = BRDF_specular_cook_torrance(d_ggx, f_schlick, g_ggx, NoL, NoV);
    vec3 specular_color = mix(vec3(specular), color * specular, metalness);

    return diffuse_color + specular_color;
}

@MAIN_PASS_PIXEL_SHADER
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(POSITION, normalize(NORMAL), light);

        result += light.color * BRDF(surface);
    }

    OUT_COLOR.rgb = result;
    OUT_COLOR.a = 1.0;
}

