#ifndef NPR_MESH_GLSL
#define NPR_MESH_GLSL

#include "NPR_Pipeline/NPR_Filters.glsl"
#include "NPR_Pipeline/NPR_Shading.glsl"

/*  META GLOBAL
    @meta: category=Shading;
*/

/* META @meta: subcategory=Simple Diffuse;*/
vec3 diffuse_shading()
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += diffuse_shading(POSITION, NORMAL, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

/* META @meta: subcategory=Simple Diffuse;*/
vec3 diffuse_half_shading()
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += diffuse_half_shading(POSITION, NORMAL, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

/* META @meta: subcategory=Simple Diffuse;*/
vec3 diffuse_gradient_shading(sampler1D gradient_texture)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += diffuse_gradient_shading(POSITION, NORMAL, gradient_texture, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

/*  META
    @meta: subcategory=Simple Specular;
    @tangent: subtype=Normal; default=radial_tangent(NORMAL, vec3(0,0,1));
    @anisotropy: default=0.5;
    @roughness: default=0.5;
*/
vec3 specular_shading(float roughness)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += specular_shading(POSITION, NORMAL, roughness, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

/*  META
    @meta: subcategory=Simple Specular;
    @roughness: default=0.5;
*/
vec3 specular_gradient_shading(sampler1D gradient_texture, float roughness)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += specular_gradient_shading(POSITION, NORMAL, roughness, gradient_texture, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

/*  META
    @meta: subcategory=Simple Specular;
    @roughness: default=0.5;
    @anisotropy: default=0.5;
    @tangent: subtype=Normal; default=radial_tangent(NORMAL, vec3(0,0,1));
*/
vec3 specular_anisotropic_shading(float roughness, float anisotropy, vec3 tangent)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += specular_anisotropic_shading(POSITION, NORMAL, tangent, anisotropy, roughness, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

/*  META
    @meta: subcategory=Simple Specular;
    @roughness: default=0.5;
    @anisotropy: default=0.5;
    @tangent: subtype=Normal; default=radial_tangent(NORMAL, vec3(0,0,1));
*/
vec3 specular_anisotropic_gradient_shading(sampler1D gradient_texture, float roughness, float anisotropy, vec3 tangent)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += specular_anisotropic_gradient_shading(POSITION, NORMAL, tangent, anisotropy, roughness, gradient_texture, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 toon_shading(float size, float gradient_size, float specularity, float offset)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += toon_shading(POSITION, NORMAL, size, gradient_size, specularity, offset, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

/*META @meta: category=Input; subcategory=Pass Info; internal=true;*/
bool is_shadow_pass()
{
    #ifdef SHADOW_PASS
    {
        return true;
    }
    #else
    {
        return false;
    }
    #endif
}
/*META @meta: category=Input; subcategory=Pass Info; internal=true;*/
bool is_pre_pass()
{
    #ifdef PRE_PASS
    {
        return true;
    }
    #else
    {
        return false;
    }
    #endif
}
/*META @meta: category=Input; subcategory=Pass Info; internal=true;*/
bool is_main_pass()
{
    #ifdef MAIN_PASS
    {
        return true;
    }
    #else
    {
        return false;
    }
    #endif
}
/*META @meta: category=Input; */
void pass_info(
    out bool main_pass,
    out bool pre_pass,
    out bool shadow_pass
    ) {
        main_pass = is_main_pass();
        pre_pass = is_pre_pass();
        shadow_pass = is_shadow_pass();
    }

#endif //NPR_MESH_GLSL
