#ifndef SHADING_MODELS_GLSL
#define SHADING_MODELS_GLSL

#include "Shading/BRDF.glsl"

/* META @meta: internal=true; */
vec3 diffuse_lit_surface(LitSurface LS)
{
    return clamp(LS.NoL, 0, 1) * LS.light_color * LS.shadow_multiply;
}

/* META @meta: internal=true; */
vec3 _diffuse_half_lit_surface_common(LitSurface LS)
{
    vec3 diffuse = vec3(map_range_clamped(LS.NoL, -1, 1, 0, 1));
    vec3 shadow = map_range_clamped(LS.shadow_multiply, vec3(0),vec3(1),vec3(0.5),vec3(1));
    return min(diffuse, shadow);
}

/* META @meta: internal=true; */
vec3 diffuse_half_lit_surface(LitSurface LS)
{
    return _diffuse_half_lit_surface_common(LS) * LS.light_color;
}

/* META @meta: internal=true; */
vec3 diffuse_gradient_lit_surface(LitSurface LS, sampler1D gradient)
{
    return rgb_gradient(gradient, _diffuse_half_lit_surface_common(LS)) * LS.light_color;
}

float _specular_shadowing(float NoL, float specular)
{
    return clamp(specular * (1.0 - pow(1.0 - max(NoL, 0), 20.0)), 0, 1);
}

/* META @meta: internal=true; */
float _specular_common_lit_surface(LitSurface LS, float roughness)
{
    float VoR = dot(LS.V, LS.R);
    VoR = _specular_shadowing(LS.NoL, VoR);
    return pow(VoR, roughness_to_shininess(roughness));
}

/* META @meta: internal=true; */
vec3 specular_lit_surface(LitSurface LS, float roughness)
{
    return _specular_common_lit_surface(LS, roughness) * LS.light_color * LS.shadow_multiply;
}

/* META @meta: internal=true; */
vec3 specular_gradient_lit_surface(LitSurface LS, float roughness, sampler1D gradient)
{
    return texture(gradient, _specular_common_lit_surface(LS, roughness)).rgb * LS.light_color * LS.shadow_multiply;
}

/* META @meta: internal=true; */
float _specular_anisotropic_lit_surface_common(LitSurface LS, vec3 tangent, float anisotropy, float roughness)
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

/* META @meta: internal=true; */
vec3 specular_anisotropic_lit_surface(LitSurface LS, vec3 tangent, float anisotropy, float roughness)
{
    return _specular_anisotropic_lit_surface_common(LS, tangent, anisotropy, roughness) * LS.light_color * LS.shadow_multiply;
}

/* META @meta: internal=true; */
vec3 specular_anisotropic_gradient_lit_surface(LitSurface LS, vec3 tangent, float anisotropy, float roughness, sampler1D gradient)
{
    return texture(gradient, _specular_anisotropic_lit_surface_common(LS, tangent, anisotropy, roughness)).rgb * LS.light_color * LS.shadow_multiply;
}

/* META @meta: internal=true; */
vec3 toon_lit_surface(LitSurface LS, float size, float gradient_size, float specularity, float offset)
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

/*  META
    @normal: subtype=Normal; default=NORMAL;
    @angle: default=0.0;
    @rim_length: default=2.0;
    @length_fallof: default=0.1;
    @thickness: default=0.1;
    @thickness_fallof: default=0.0;
*/
float rim_light(vec3 normal, float angle, float rim_length, float length_falloff, float thickness, float thickness_falloff)
{
    vec2 angle_vec = vec2(cos(angle), sin(angle));

    vec3 r = cross(transform_normal(CAMERA, view_direction()), transform_normal(CAMERA, normal));
    vec2 r2d = normalize(r.xy);

    float angle_dot = dot(r2d, angle_vec);
    angle_dot = angle_dot * 0.5 + 0.5;
    float facing_dot = dot(view_direction(), normal);
    facing_dot = 1.0 - facing_dot;

    length_falloff = max(1e-6, length_falloff);
    thickness_falloff = max(1e-6, thickness_falloff);

    float angle_result = map_range_clamped(angle_dot, 1.0 - rim_length, 1.0 - (rim_length - length_falloff), 0.0, 1.0);
    float facing_result = map_range_clamped(facing_dot * angle_result, 1.0 - thickness, 1.0 - (thickness - thickness_falloff), 0.0, 1.0);

    return angle_result * facing_result;
}

#endif //SHADING_MODELS_GLSL
