#ifndef NPR_SHADING2_GLSL
#define NPR_SHADING2_GLSL

#include "NPR_Lighting.glsl"
#include "Shading/ShadingModels.glsl"

/*  META GLOBAL
    @meta: category=Shading;
*/

void _shadow_params(int enum_value, out bool shadows, out bool self_shadows)
{
    #ifdef IS_MESH_SHADER
    {
        shadows = enum_value == 0 ? Settings.Receive_Shadow : enum_value < 3;
        self_shadows = enum_value == 0 ? Settings.Self_Shadow : enum_value == 1;
    }
    #else
    {
        shadows = enum_value < 2;
        self_shadows = enum_value == 0;
    }
    #endif
}

#ifdef IS_MESH_SHADER
/*  META
    @meta: label=Diffuse;
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @light_groups: default=MATERIAL_LIGHT_GROUPS;
    @shadows: subtype=ENUM(Inherit from Material,Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#else
/*  META
    @meta: label=Diffuse;
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @light_groups: default=ivec4(1,0,0,0);
    @shadows: subtype=ENUM(Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#endif
vec3 NPR_diffuse_shading(vec3 position, vec3 normal,
    sampler1D gradient, bool full_range, float offset,
    bool max_contribution, ivec4 light_groups, int shadows)
{
    bool shadow;
    bool self_shadow;
    _shadow_params(shadows, shadow, self_shadow);
    
    vec3 result = vec3(0,0,0);
    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        for(int group_index = 0; group_index < 4; group_index++)
        {
            if(LIGHT_GROUP_INDEX(i) != light_groups[group_index])
            {
                continue;
            }
            Light L = LIGHTS.lights[i];
            LitSurface LS = npr_lit_surface(position, normal, ID.x, L, i, shadow, self_shadow);

            if(!full_range && LS.NoL < 0)
            {
                continue;
            }
            
            float lambert = LS.NoL;
            vec3 shadow_multiply = LS.shadow_multiply;
            if(full_range)
            {
                lambert = map_range(LS.NoL, -1, 1, 0, 1);
                shadow_multiply = map_range_clamped(LS.shadow_multiply, vec3(0),vec3(1),vec3(0.5),vec3(1));
            }
            lambert = saturate(lambert + offset);
            
            vec3 diffuse = rgb_gradient(gradient, min(vec3(lambert), shadow_multiply)) * LS.light_color;

            if(max_contribution)
            {
                result = max(result, diffuse);
            }
            else
            {
                result += diffuse;
            }
        }
    }
    
    return result;
}

#ifdef IS_MESH_SHADER
/*  META
    @meta: label=Specular;
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @tangent: subtype=Normal; default=radial_tangent(transform_normal(inverse(MODEL), NORMAL), vec3(0,0,1));
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @anisotropy: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @roughness: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @light_groups: default=MATERIAL_LIGHT_GROUPS;
    @shadows: subtype=ENUM(Inherit from Material,Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#else
/*  META
    @meta: label=Specular;
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @tangent: subtype=Normal; default=radial_tangent(transform_normal(inverse(MODEL), NORMAL), vec3(0,0,1));
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @anisotropy: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @roughness: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @light_groups: default=ivec4(1,0,0,0);
    @shadows: subtype=ENUM(Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#endif
vec3 NPR_specular_shading(vec3 position, vec3 normal, vec3 tangent,
    sampler1D gradient, float offset, float roughness, float anisotropy,
    bool max_contribution, ivec4 light_groups, int shadows)
{
    bool shadow;
    bool self_shadow;
    _shadow_params(shadows, shadow, self_shadow);
    
    vec3 result = vec3(0,0,0);
    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        for(int group_index = 0; group_index < 4; group_index++)
        {
            if(LIGHT_GROUP_INDEX(i) != light_groups[group_index])
            {
                continue;
            }
            Light L = LIGHTS.lights[i];
            LitSurface LS = npr_lit_surface(position, normal, ID.x, L, i, shadow, self_shadow);

            if(LS.NoL < 0)
            {
                continue;
            }

            float NoH = dot(normal, LS.H);
            
            vec3 bitangent = normalize(cross(normal, tangent));
            float XoH = dot(LS.H, tangent);
            float YoH = dot(LS.H, bitangent);

            vec2 a = vec2(anisotropy, 1.0 - anisotropy) * roughness;

            float custom_ggx = (1.0 / (pow((XoH*XoH) / (a.x*a.x) + (YoH*YoH) / (a.y*a.y) + NoH*NoH, 3.0)));
            //custom_ggx = (1.0 / (pow(abs(XoH) / (a.x) + abs(YoH) / (a.y) + NoH*NoH, 5.0))); Looks cool!
            
            //minimal geometric shadowing
            custom_ggx *= saturate(pow(LS.NoL*3,3));
            
            custom_ggx = saturate(custom_ggx + offset);

            vec4 gradient_sample = texture(gradient, custom_ggx);
            gradient_sample *= gradient_sample.a;
            vec3 specular = gradient_sample.rgb * LS.light_color * LS.shadow_multiply;
            
            if(max_contribution)
            {
                result = max(result, specular);
            }
            else
            {
                result += specular;
            }
        }
    }
    
    return result;
}

#endif //NPR_SHADING2_GLSL

