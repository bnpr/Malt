#ifndef BRDF_GLSL
#define BRDF_GLSL

// The following formulas follow the naming conventions explained in the LitSurface struct declaration (Lighing.glsl)
// X is for tangent and Y for bitangent. (ie. XoH means dot(tangent, halfway_vector))
// (a) parameter stands for roughness factor (0..1)
// Dot products should be clamped to (MIN_DOT..1)

//Division by PI has been factored out for a more intuitive artistic workflow
//https://seblagarde.wordpress.com/2012/01/08/pi-or-not-to-pi-in-game-lighting-equation/

//UTILS

#define MIN_DOT 1e-10

/* META @meta: internal=true; */
float safe_dot(vec3 a, vec3 b)
{
    return clamp(dot(a,b), MIN_DOT, 1.0);
}

/* META @meta: internal=true; */
float roughness_to_shininess(float roughness)
{
    return 2.0 / pow(max(0.1, roughness), 3);
}

// DIFFUSE BRDFs

/* META @meta: internal=true; */
float BRDF_lambert(float NoL)
{
    return NoL;
}

float F_schlick(float VoH, float F0, float F90); //Forward declaration, definition in Fresnel section

/* META @meta: internal=true; */
float BRDF_burley(float NoL, float NoV, float VoH, float a)
{
    //https://disney-animation.s3.amazonaws.com/library/s2012_pbs_disney_brdf_notes_v2.pdf
    float f90 = 0.5 + 2.0 * a * VoH*VoH;

    return F_schlick(NoL, 1.0, f90) * F_schlick(NoV, 1.0, f90) * NoL;
}

/* META @meta: internal=true; */
float BRDF_oren_nayar(float NoL, float NoV, float LoV, float a)
{
    //https://mimosa-pudica.net/improved-oren-nayar.html
    float s = LoV - NoL * NoV;
    float t = s <= 0 ? 1.0 : max(NoL, NoV);
    float A = 1.0 - 0.5 * (a*a / (a*a + 0.33) + 0.17 * (a*a / (a*a + 0.13)));
    float B = 0.45 * (a*a / (a*a + 0.09));

    return NoL * (A + B * (s / t));
}

// SPECULAR BRDFs
//http://graphicrants.blogspot.com/2013/08/specular-brdf-reference.html

/* META @meta: internal=true; */
float BRDF_specular_cook_torrance(float D, float F, float G, float NoL, float NoV)
{
    return (D * F * G) / (4.0 * NoL * NoV) * NoL * PI;
}

// Specular Normal Distribution Functions

/* META @meta: internal=true; */
float D_phong(float VoR, float a)
{
    return pow(VoR, roughness_to_shininess(a));
}

/* META @meta: internal=true; */
float D_blinn_phong(float NoH, float a)
{
    return pow(NoH, roughness_to_shininess(a));
}

/* META @meta: internal=true; */
float D_ward(float NoL, float NoV, float NoH, float XoH, float YoH, float aX, float aY)
{
    float e = -2.0 * ((pow(XoH / aX, 2) + pow(YoH / aY, 2)) / (1.0 + NoH));
    return (1.0 / sqrt(NoL * NoV)) * (NoL / (4.0 * PI * aX * aY)) * exp(e);
}

/* META @meta: internal=true; */
float D_beckmann(float NoH, float a)
{
    return (1.0 / (PI * a*a * pow(NoH, 4.0))) * exp((NoH*NoH - 1.0) / (a*a * NoH*NoH));
}

/* META @meta: internal=true; */
float D_GGX(float NoH, float a)
{
    return (a*a) / (PI * pow(NoH*NoH * (a*a - 1.0) + 1.0, 2.0));
}

/* META @meta: internal=true; */
float D_GGX_anisotropic(float NoH, float XoH, float YoH, float ax, float ay)
{
    return (1.0 / (PI * ax*ay)) * (1.0 / (pow((XoH*XoH) / (ax*ax) + (YoH*YoH) / (ay*ay) + NoH*NoH, 2.0)));
}

// Specular Geometric Shadowing Functions

/* META @meta: internal=true; */
float G_implicit(float NoL, float NoV)
{
    return NoL*NoV;
}

/* META @meta: internal=true; */
float G_neumann(float NoL, float NoV)
{
    return (NoL*NoV) / max(NoL, NoV);
}

/* META @meta: internal=true; */
float G_cook_torrance(float NoH, float NoV, float NoL, float VoH)
{
    return min(1.0, min((2.0 * NoH * NoV) / VoH, (2.0 * NoH * NoL) / VoH));
}

/* META @meta: internal=true; */
float G_kelemen(float NoL, float NoV, float VoH)
{
    return (NoL*NoV) / VoH*VoH;
}

float _G1_beckmann(float NoLV, float a)
{
    float c = NoLV / (a * sqrt(1.0 - NoLV*NoLV));

    if(c >= 1.6) return 1.0;

    return (3.535*c + 2.181*c*c) / (1.0 + 2.276*c + 2.577*c*c);
}

/* META @meta: internal=true; */
float G_beckmann(float NoL, float NoV, float a)
{
    return _G1_beckmann(NoL, a) * _G1_beckmann(NoV, a);
}

float _G1_GGX(float NoLV, float a)
{
    return (2 * NoLV) / (NoLV + (sqrt(a*a + (1 - a*a) * NoLV*NoLV)));
}

/* META @meta: internal=true; */
float G_GGX(float NoL, float NoV, float a)
{
    return _G1_GGX(NoL, a) * _G1_GGX(NoV, a);
}

// Specular Fresnel Functions

/* META @meta: internal=true; */
float F_schlick(float VoH, float F0, float F90)
{
    // https://en.wikipedia.org/wiki/Schlick%27s_approximation
    return F0 + (F90 - F0) * pow(1.0 - VoH, 5.0);
}

/* META @meta: internal=true; */
float F_cook_torrance(float VoH, float F0)
{
    float n = (1.0 + sqrt(F0)) / (1.0 - sqrt(F0));
    float c = VoH;
    float g = sqrt(n*n + c*c - 1.0);

    float A = (g - c) / (g + c);
    float B = ((g + c) * c - 1.0) / ((g - c) * c + 1.0);

    return 0.5 * A*A * (1.0 + B*B);
}

#endif //BRDF_GLSL

