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
    @meta: label=Color Ramp; subcategory=NPR Diffuse;
    @base_color: default=vec3(0);
    @color: default=vec3(1);
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @light_groups: default=MATERIAL_LIGHT_GROUPS;
    @shadow_mode: subtype=ENUM(Multiply,Remap); default=0;
    @shadows: subtype=ENUM(Inherit from Material,Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#else
/*  META
    @meta: label=Color Ramp; subcategory=NPR Diffuse;
    @base_color: default=vec3(0);
    @color: default=vec3(1);
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @light_groups: default=ivec4(1,0,0,0);
    @shadow_mode: subtype=ENUM(Multiply,Remap); default=0;
    @shadows: subtype=ENUM(Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#endif
vec3 NPR_diffuse_shading(
    vec3 base_color,
    vec3 color,
    sampler1D gradient,
    float offset,
    bool full_range,
    bool max_contribution,
    //int shadow_mode,
    int shadows,
    ivec4 light_groups,
    vec3 position,
    vec3 normal
)
{
    bool shadow;
    bool self_shadow;
    _shadow_params(shadows, shadow, self_shadow);

    if(full_range)
    {
        self_shadow = false;
    }
    
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
            if(full_range)
            {
                lambert = map_range(LS.NoL, -1, 1, 0, 1);
            }
            lambert = saturate(lambert + offset);

            vec4 gradient_sample = texture(gradient, lambert);
            gradient_sample *= gradient_sample.a;
            vec3 diffuse = gradient_sample.rgb * LS.light_color * LS.shadow_multiply;
            /*
            vec3 diffuse;
            vec3 shadow_multiply = LS.shadow_multiply;
            if(shadow_mode == 0)//Multiply
            {
                diffuse = texture(gradient, lambert).rgb * shadow_multiply * LS.light_color;
            }
            else if(shadow_mode == 1)//Remap
            {                
                if(full_range)
                {
                    shadow_multiply = map_range_clamped(LS.shadow_multiply, vec3(0), vec3(1), vec3(0.5), vec3(1));
                }
                diffuse = rgb_gradient(gradient, min(vec3(lambert), shadow_multiply)) * LS.light_color;
            }
            */
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
    
    return mix(base_color, color, result);
}

vec3 _map_gradient(float size, float gradient_size, vec3 uvw)
{
    if(gradient_size > 0.0)
    {
        return map_range_clamped(uvw, vec3(1.0 - size), vec3(1.0 - size + gradient_size), vec3(0.0), vec3(1.0));
    }
    else
    {
        return vec3(greaterThan(uvw, vec3(1.0 - size)));
    }
}

#ifdef IS_MESH_SHADER
/*  META
    @meta: label=Color Layer; subcategory=NPR Diffuse;
    @base_color: default=vec3(0);
    @color: default=vec3(1);
    @size: subtype=Slider; min=-0.0; max=1.0; default=1.0;
    @gradient_size: subtype=Slider; min=0.0; max=1.0; default=0.1;
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @light_groups: default=MATERIAL_LIGHT_GROUPS;
    @shadow_mode: subtype=ENUM(Multiply,Remap); default=0;
    @shadows: subtype=ENUM(Inherit from Material,Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#else
/*  META
    @meta: label=Color Layer; subcategory=NPR Diffuse;
    @base_color: default=vec3(0);
    @color: default=vec3(1);
    @size: subtype=Slider; min=-0.0; max=1.0; default=1.0;
    @gradient_size: subtype=Slider; min=0.0; max=1.0; default=0.1;
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @light_groups: default=ivec4(1,0,0,0);
    @shadow_mode: subtype=ENUM(Multiply,Remap); default=0;
    @shadows: subtype=ENUM(Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#endif
vec3 NPR_diffuse_layer(
    vec3 base_color,
    vec3 color,
    float size,
    float gradient_size,
    float offset,
    bool full_range,
    //int shadow_mode,
    bool max_contribution,
    int shadows,
    ivec4 light_groups,
    vec3 position,
    vec3 normal
)
{
    bool shadow;
    bool self_shadow;
    _shadow_params(shadows, shadow, self_shadow);
    if(full_range)
    {
        self_shadow = false;
    }

    size = saturate(size + offset);
    gradient_size = min(size, gradient_size);
    
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
            if(full_range)
            {
                lambert = map_range(LS.NoL, -1.0, 1.0, 0.0, 1.0);
            }

            vec3 diffuse = _map_gradient(size, gradient_size, vec3(lambert)) * LS.light_color * LS.shadow_multiply;
            /*
            vec3 diffuse;
            vec3 shadow_multiply = LS.shadow_multiply;
            if(shadow_mode == 0)//Multiply
            {
                diffuse = _map_gradient(size, gradient_size, vec3(lambert)) * shadow_multiply * LS.light_color;
            }
            else if(shadow_mode == 1)//Remap
            {                
                if(full_range)
                {
                    shadow_multiply = map_range_clamped(LS.shadow_multiply, vec3(0), vec3(1), vec3(0.5), vec3(1));
                }
                diffuse = _map_gradient(size, gradient_size, min(vec3(lambert), shadow_multiply)) * LS.light_color;
            }
            */
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
    
    return mix(base_color, color, result);
}

#ifdef IS_MESH_SHADER
/*  META
    @meta: label=Color Ramp; subcategory=NPR Specular;
    @base_color: default=vec3(0);
    @color: default=vec3(1);
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @tangent: subtype=Normal; default=radial_tangent(NORMAL, vec3(0,0,1));
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @anisotropy: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @roughness: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @light_groups: default=MATERIAL_LIGHT_GROUPS;
    @shadows: subtype=ENUM(Inherit from Material,Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#else
/*  META
    @meta: label=Color Ramp; subcategory=NPR Specular;
    @base_color: default=vec3(0);
    @color: default=vec3(1);
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @tangent: subtype=Normal; default=radial_tangent(NORMAL, vec3(0,0,1));
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @anisotropy: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @roughness: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @light_groups: default=ivec4(1,0,0,0);
    @shadows: subtype=ENUM(Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#endif
vec3 NPR_specular_shading(
    vec3 base_color,
    vec3 color,
    sampler1D gradient,
    float offset,
    float roughness,
    float anisotropy,
    bool max_contribution,
    int shadows,
    ivec4 light_groups,
    vec3 position,
    vec3 normal,
    vec3 tangent
)
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
            
            //minimal geometric shadowing
            custom_ggx *= 1.0 - pow(1.0 - LS.NoL, 5);
            
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
    
    return mix(base_color, color, result);
}

#ifdef IS_MESH_SHADER
/*  META
    @meta: label=Color Layer; subcategory=NPR Specular;
    @base_color: default=vec3(0);
    @color: default=vec3(1);
    @size: subtype=Slider; min=-0.0; max=1.0; default=1.0;
    @gradient_size: subtype=Slider; min=0.0; max=1.0; default=0.1;
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @tangent: subtype=Normal; default=radial_tangent(NORMAL, vec3(0,0,1));
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @anisotropy: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @roughness: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @light_groups: default=MATERIAL_LIGHT_GROUPS;
    @shadows: subtype=ENUM(Inherit from Material,Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#else
/*  META
    @meta: label=Color Layer; subcategory=NPR Specular;
    @base_color: default=vec3(0);
    @color: default=vec3(1);
    @size: subtype=Slider; min=-0.0; max=1.0; default=1.0;
    @gradient_size: subtype=Slider; min=0.0; max=1.0; default=0.1;
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @tangent: subtype=Normal; default=radial_tangent(NORMAL, vec3(0,0,1));
    @offset: subtype=Slider; min=-1.0; max=1.0; default=0.0;
    @anisotropy: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @roughness: subtype=Slider; min=0.0; max=1.0; default=0.5;
    @light_groups: default=ivec4(1,0,0,0);
    @shadows: subtype=ENUM(Enable Shadows,Disable Self-Shadows,Disable Shadows); default=0;
*/
#endif
vec3 NPR_specular_layer(
    vec3 base_color,
    vec3 color,
    float size,
    float gradient_size,
    float offset,
    float roughness,
    float anisotropy,
    bool max_contribution,
    int shadows,
    ivec4 light_groups,
    vec3 position,
    vec3 normal,
    vec3 tangent
)
{
    bool shadow;
    bool self_shadow;
    _shadow_params(shadows, shadow, self_shadow);

    size = saturate(size + offset) * 0.99;
    gradient_size = min(size, gradient_size);
    
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
            
            //minimal geometric shadowing
            custom_ggx *= 1.0 - pow(1.0 - LS.NoL, 5);

            vec3 specular = _map_gradient(size, gradient_size, vec3(custom_ggx)) * LS.light_color * LS.shadow_multiply;
            
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
    
    return mix(base_color, color, result);
}

#endif //NPR_SHADING2_GLSL
