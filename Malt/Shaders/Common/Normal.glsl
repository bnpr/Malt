#ifndef COMMON_NORMAL_GLSL
#define COMMON_NORMAL_GLSL

#include "Common.glsl"

vec3 true_normal()
{
    #ifndef CUSTOM_TRUE_NORMAL
    {
        #ifdef PIXEL_SHADER
        {
            return normalize(cross(dFdx(POSITION), dFdy(POSITION)));
        }
        #endif //PIXEL_SHADER
        
        return NORMAL;
    }
    #else
    {
        return CUSTOM_TRUE_NORMAL;
    }
    #endif //CUSTOM_TRUE_NORMAL
}

float facing()
{
    return dot(NORMAL, -view_direction());
}

bool is_front_facing()
{
    #ifdef PIXEL_SHADER
    {
        return gl_FrontFacing;
    }
    #endif
    return facing() > 0;
}

vec4 compute_tangent(vec2 uv)
{
    // Copyright (c) 2020 mmikk. MIT License
    // http://jcgt.org/published/0009/03/04/
    #ifdef PIXEL_SHADER
    {
        vec3 normal = normalize(NORMAL);
        
        vec3 position_dx = dFdx(POSITION);
        vec3 position_dy = dFdy(POSITION);

        vec3 sigma_x = position_dx - dot(position_dx, normal) * normal;
        vec3 sigma_y = position_dy - dot(position_dy, normal) * normal;

        float flip_sign = dot(position_dy, cross(normal, position_dx)) < 0 ? -1 : 1;
        
        vec2 uv_dx = dFdx(uv);
        vec2 uv_dy = dFdy(uv);

        float determinant = dot(uv_dx, vec2(uv_dy.y, -uv_dy.x));
        float determinant_sign = determinant < 0.0 ? -1.0 : 1.0;
    
        // inverse represents (dXds, dYds), but we don't divide
        // by the determinant. Instead, we scale by the sign.
        vec2 inverse = determinant_sign * vec2(uv_dy.y, -uv_dx.y); 
        
        vec3 tangent = sigma_x * inverse.x + sigma_y * inverse.y;
        if (abs(determinant) > 0.0)
        {
            tangent = normalize(tangent);
        }

        return vec4(tangent, (determinant_sign * flip_sign));
    }
    #endif

    return vec4(0);
}

vec3 get_tangent(int uv_index)
{
    if(PRECOMPUTED_TANGENTS && uv_index == 0) return TANGENT;
    return compute_tangent(UV[uv_index]).xyz;
}

vec3 get_bitangent(int uv_index)
{
    if(PRECOMPUTED_TANGENTS && uv_index == 0) return BITANGENT;
    vec4 T = compute_tangent(UV[uv_index]);
    return normalize(cross(NORMAL, T.xyz) * T.w);
}

mat3 get_TBN(int uv_index)
{
    mat3 TBN = mat3(get_tangent(uv_index), get_bitangent(uv_index), NORMAL);
    #ifdef PIXEL_SHADER
    {
        if(!gl_FrontFacing)
        {
            TBN[2] *= -1;
        }
    }
    #endif //PIXEL_SHADER
    return TBN;
}

vec3 sample_normal_map_ex(sampler2D normal_texture, mat3 TBN, vec2 uv)
{
    vec3 tangent = texture(normal_texture, uv).xyz;
    tangent = tangent * 2.0 - 1.0;
    return normalize(TBN * tangent);
}

vec3 sample_normal_map(sampler2D normal_texture, int uv_index, vec2 uv)
{
    return sample_normal_map_ex(normal_texture, get_TBN(uv_index), uv);
}

/*  META
    @normal: subtype=Normal; default=NORMAL;
    @axis: subtype=Normal; default=(0,0,1);
*/
vec3 radial_tangent(vec3 normal, vec3 axis)
{
    return normalize(cross(axis, normal));
}

/*  META
    @custom_normal: subtype=Normal; default=NORMAL;
*/
vec3 surface_gradient_from_normal(vec3 custom_normal)
{
    // Copyright (c) 2020 mmikk. MIT License
    // http://jcgt.org/published/0009/03/04/
    const float epsilon = 1.192092896e-07f;
    float NoC = dot(NORMAL, custom_normal);
    return (NoC * NORMAL - custom_normal) / max(epsilon, abs(NoC));
}

/*  META
    @surface_gradient: subtype=Vector; default=vec3(0);
*/
vec3 normal_from_surface_gradient(vec3 surface_gradient)
{
    // Copyright (c) 2020 mmikk. MIT License
    // http://jcgt.org/published/0009/03/04/
    return normalize(NORMAL - surface_gradient);
}

#endif //COMMON_NORMAL_GLSL
