//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

/// NPR Pipeline for mesh materials.
/// Includes a simplified API for writing shaders.

#include "NPR_Intellisense.glsl"
#include "Common/Hash.glsl"
#include "Common.glsl"

// Global material settings. Can be modified in the material panel UI
struct NPR_Settings
{
    bool Receive_Shadow;
    bool Self_Shadow;
    bool Transparency;
    bool Transparency_Single_Layer;
    float Vertex_Displacement_Offset;
};

uniform NPR_Settings Settings = NPR_Settings(true, true, false, false, 0.001);

uniform ivec4 MATERIAL_LIGHT_GROUPS;

struct Vertex
{
    vec3 position;
    vec3 normal;
    uvec4 id;
    vec3 tangent;
    vec3 bitangent;
    vec2 uv[4];
    vec4 vertex_color[4];
};

struct PrePassOutput
{
    vec3 normal;
    float depth_offset;
    bool offset_position;
    uvec4 id;
    vec4 surface_color;
};

#ifdef VERTEX_SHADER

void COMMON_VERTEX_SHADER(inout Vertex V);

#ifndef CUSTOM_VERTEX_SHADER
void COMMON_VERTEX_SHADER(inout Vertex V){}
#endif

vec3 VERTEX_DISPLACEMENT_SHADER(Vertex V);

#ifndef CUSTOM_VERTEX_DISPLACEMENT
vec3 VERTEX_DISPLACEMENT_SHADER(Vertex V){ return vec3(0); }
#endif

#ifndef VERTEX_DISPLACEMENT_OFFSET
    #define VERTEX_DISPLACEMENT_OFFSET 0.1
#endif

#ifndef CUSTOM_MAIN
void main()
{
    DEFAULT_VERTEX_SHADER();

    Vertex V;
    V.position = POSITION;
    V.normal = NORMAL;
    V.tangent = TANGENT;
    V.bitangent = BITANGENT;
    V.uv = UV;
    V.color = COLOR;
    V.id.r = ID;
    
    COMMON_VERTEX_SHADER(V);

    POSITION = V.position;
    NORMAL = V.normal;
    TANGENT = V.tangent;
    BITANGENT = V.bitangent;
    UV = V.uv;
    COLOR = V.color;
    ID = V.ID TODO

    #ifdef CUSTOM_VERTEX_DISPLACEMENT
    {
        vec3 displaced_position = POSITION + VERTEX_DISPLACEMENT_SHADER(V);
        
        if(!PRECOMPUTED_TANGENTS)
        {
            vec3 axis = vec3(0,0,1);
            axis = abs(dot(axis, NORMAL)) < 0.99 ? axis : vec3(1,0,0);
            vec3 tangent = normalize(cross(axis, NORMAL));
            TANGENT = tangent;
            BITANGENT = normalize(cross(NORMAL, tangent));
        }
        
        Vertex v = V;

        v.position = POSITION + TANGENT * Settingv.Vertex_Displacement_Offset;
        vec3 displaced_tangent = v.position + VERTEX_DISPLACEMENT_SHADER(s);
        TANGENT = normalize(displaced_tangent - displaced_position);

        v.position = POSITION + BITANGENT * Settingv.Vertex_Displacement_Offset;
        vec3 displaced_bitangent = v.position + VERTEX_DISPLACEMENT_SHADER(s);
        BITANGENT = normalize(displaced_bitangent - displaced_position);
        
        POSITION = displaced_position;
        NORMAL = normalize(cross(TANGENT, BITANGENT));
        
        if(!PRECOMPUTED_TANGENTS)
        {
            TANGENT = vec3(0);
            BITANGENT = vec3(0);
        }
    }
    #endif
    
    VERTEX_SETUP_OUTPUT();
}
#endif //NDEF CUSTOM_MAIN

#endif //VERTEX_SHADER

#ifdef PIXEL_SHADER

uniform sampler2D IN_OPAQUE_COLOR;
uniform sampler2D IN_OPAQUE_DEPTH;
uniform sampler2D IN_TRANSPARENT_DEPTH;
uniform usampler2D IN_LAST_ID;

#ifdef SHADOW_PASS
layout (location = 0) out uint OUT_ID;
layout (location = 1) out vec3 OUT_SHADOW_MULTIPLY_COLOR;
#endif //PRE_PASS

#ifdef PRE_PASS
layout (location = 0) out vec4 OUT_NORMAL_DEPTH;
layout (location = 1) out uvec4 OUT_ID;
#endif //PRE_PASS

#ifdef MAIN_PASS
uniform sampler2D IN_NORMAL_DEPTH;
uniform usampler2D IN_ID;

layout (location = 0) out vec4 OUT_COLOR;
#endif //MAIN_PASS

#ifndef CUSTOM_MAIN

void PRE_PASS_PIXEL_SHADER(inout PrePassOutput PO);

void MAIN_PASS_PIXEL_SHADER();

void main()
{
    PIXEL_SETUP_INPUT();

    PrePassOutput PPO;
    PPO.normal = NORMAL;
    PPO.depth_offset = 0;
    PPO.offset_position = true;
    PPO.id = uvec4(ID,0,0,0);
    PPO.surface_color = vec4(0,0,0,1);

    PRE_PASS_PIXEL_SHADER(PPO);

    if(PPO.surface_color.a == 0)
    {
        discard;
    }
    else if(!Settings.Transparency)
    {
        PPO.surface_color.a = 1.0;
    }

    float depth = gl_FragCoord.z;
    vec3 offset_position = POSITION - view_direction() * PPO.depth_offset;

    #ifdef SHADOW_PASS
    {
        if(!PPO.offset_position)
        {
            PPO.depth_offset = 0;
        }
    }
    #endif

    if(PPO.depth_offset != 0)
    {
        depth = project_point(PROJECTION * CAMERA, offset_position).z;
        float far = gl_DepthRange.far;
        float near = gl_DepthRange.near;
        gl_FragDepth = (((far-near) * depth) + near + far) / 2.0;
    }

    #ifdef SHADOW_PASS
    {
        OUT_ID = PPO.id.r;

        if(Settings.Transparency)
        {
            float pass_through = hash(vec4(POSITION, SAMPLE_COUNT)).x;
            if(pass_through > PPO.surface_color.a)
            {
                discard;
            }
            //TODO: Take alpha probability into account for multiply color
            OUT_SHADOW_MULTIPLY_COLOR = PPO.surface_color.rgb * saturate(1.0 - PPO.surface_color.a);
        }
    }
    #endif
    
    #ifdef PRE_PASS
    {
        if(Settings.Transparency)
        {
            float opaque_depth = texelFetch(IN_OPAQUE_DEPTH, ivec2(gl_FragCoord.xy), 0).x;
            float transparent_depth = texelFetch(IN_TRANSPARENT_DEPTH, ivec2(gl_FragCoord.xy), 0).x;
            
            if(depth >= opaque_depth || depth <= transparent_depth)
            {
                discard;
            }

            if(Settings.Transparency_Single_Layer)
            {
                if(PO.id.r == texelFetch(IN_LAST_ID, ivec2(gl_FragCoord.xy), 0).x)
                {
                    discard;
                }
            }
        }

        OUT_NORMAL_DEPTH.xyz = PPO.normal;
        OUT_NORMAL_DEPTH.w = depth;
        OUT_ID = PPO.id;
    }
    #endif

    #ifdef MAIN_PASS
    {
        if(PPO.offset_position)
        {
            POSITION = offset_position;
        }
        NORMAL = texelFetch(IN_NORMAL_DEPTH, ivec2(gl_FragCoord.xy), 0).xyz;
        ID = texelFetch(IN_ID, ivec2(gl_FragCoord.xy), 0).xyz;

        MAIN_PASS_PIXEL_SHADER();
    }
    #endif
}

#endif //NDEF CUSTOM_MAIN

#endif //PIXEL_SHADER

//NPR PIPELINE SIMPLIFIED API

#include "NPR_Shading.glsl"
#include "Shading/Rim.glsl"
#include "Filters/AO.glsl"
#include "Filters/Bevel.glsl"
#include "Filters/Curvature.glsl"
#include "Filters/Line.glsl"

vec3 get_diffuse()
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += scene_diffuse(POSITION, get_normal(), MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 get_diffuse_half()
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += scene_diffuse_half(POSITION, get_normal(), MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 get_diffuse_gradient(sampler1D gradient_texture)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += scene_diffuse_gradient(POSITION, get_normal(), gradient_texture, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 get_specular(float roughness)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += scene_specular(POSITION, get_normal(), roughness, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 get_specular_gradient(sampler1D gradient_texture, float roughness)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += scene_specular_gradient(POSITION, get_normal(), roughness, gradient_texture, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 get_specular_anisotropic(float roughness, float anisotropy, vec3 tangent)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += scene_specular_anisotropic(POSITION, get_normal(), tangent, anisotropy, roughness, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 get_specular_anisotropic_gradient(sampler1D gradient_texture, float roughness, float anisotropy, vec3 tangent)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += scene_specular_anisotropic_gradient(POSITION, get_normal(), tangent, anisotropy, roughness, gradient_texture, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 get_toon(float size, float gradient_size, float specularity, float offset)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += scene_toon(POSITION, get_normal(), size, gradient_size, specularity, offset, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

float get_ao(int samples, float radius)
{
    #if defined(PIXEL_SHADER) && defined(MAIN_PASS)
    {
        float ao = ao_ex(IN_NORMAL_DEPTH, 3, POSITION, normalize(NORMAL), samples, radius, 5.0, 0);
        ao = pow(ao, 5.0); //Pow for more contrast
        //TODO: For some reason, using pow causes some values to go below 0 ?!?!?!?
        ao = max(0, ao);
        return ao;
    }
    #else
    {
        return 1.0;
    }
    #endif
}

float get_curvature()
{
    #if defined(PIXEL_SHADER) && defined(MAIN_PASS)
    {
        vec3 x = transform_normal(inverse(CAMERA), vec3(1,0,0));
        vec3 y = transform_normal(inverse(CAMERA), vec3(0,1,0));
        return curvature(IN_NORMAL_DEPTH, screen_uv(), 1.0, x, y);
    }
    #else
    {
        return 0.5;
    }
    #endif
}

float get_surface_curvature(float depth_range /*0.5*/)
{
    #if defined(PIXEL_SHADER) && defined(MAIN_PASS)
    {
        vec3 x = transform_normal(inverse(CAMERA), vec3(1,0,0));
        vec3 y = transform_normal(inverse(CAMERA), vec3(0,1,0));
        return surface_curvature(IN_NORMAL_DEPTH, IN_NORMAL_DEPTH, 3, screen_uv(), 1.0, x, y, depth_range);
    }
    #else
    {
        return 0.5;
    }
    #endif
}

vec3 get_soft_bevel(int samples, float radius, float distribution_pow, bool only_self)
{
    #if defined(PIXEL_SHADER) && defined(MAIN_PASS)
    {
        uint id = texture(IN_ID, screen_uv())[0];
        return bevel_ex(
            IN_NORMAL_DEPTH, IN_NORMAL_DEPTH, 3,
            id, only_self, IN_ID, 0,
            samples, radius, distribution_pow,
            false, 1);
    }
    #endif
    return NORMAL;
}

vec3 get_hard_bevel(int samples, float radius, float distribution_pow, bool only_self, float max_dot)
{
    #if defined(PIXEL_SHADER) && defined(MAIN_PASS)
    {
        uint id = texture(IN_ID, screen_uv())[0];
        return bevel_ex(
            IN_NORMAL_DEPTH, IN_NORMAL_DEPTH, 3,
            id, only_self, IN_ID, 0,
            samples, radius, distribution_pow,
            true, max_dot);
    }
    #endif
    return NORMAL;
}

bool get_is_front_facing()
{
    #ifdef PIXEL_SHADER
    {
        return gl_FrontFacing;
    }
    #endif
    return true;
}

float get_facing()
{
    float d = dot(get_normal(), view_direction());
    return d;
    return clamp(d, 0.0, 1.0);
}

float get_fresnel()
{
    return 1.0 - get_facing();
}

vec4 get_matcap(sampler2D matcap_texture)
{
    return texture(matcap_texture, matcap_uv(get_normal()));
}

float get_rim_light(float angle, float rim_length, float thickness, float thickness_falloff)
{
    return rim_light(get_normal(), angle * DEGREES_TO_RADIANS, rim_length, rim_length, thickness, thickness_falloff);
}

LineDetectionOutput get_line_detection()
{
    LineDetectionOutput result;

    #if defined(PIXEL_SHADER) && defined(MAIN_PASS)
    {
        result = line_detection(
            POSITION,
            get_normal(), true_normal(),
            1,
            1,
            LINE_DEPTH_MODE_NEAR,
            screen_uv(),
            IN_NORMAL_DEPTH,
            3,
            IN_NORMAL_DEPTH,
            IN_ID
        );
    }
    #endif

    return result;
}

float get_line_simple(float width, float depth_threshold, float normal_threshold)
{
    #if defined(PIXEL_SHADER) && defined(MAIN_PASS)
    {
        LineDetectionOutput lo = get_line_detection();

        bool line = any(lo.id_boundary) || 
                    lo.delta_distance > depth_threshold ||
                    lo.delta_angle > normal_threshold;
        
        return float(line) * width;
    }
    #else
    {
        return 0.0;
    }
    #endif
}

float get_line_advanced(
    float id_boundary_width,
    float min_depth_threshold, float max_depth_threshold, float min_depth_width, float max_depth_width,
    float min_angle_threshold, float max_angle_threshold, float min_angle_width, float max_angle_width
)
{
    #if defined(PIXEL_SHADER) && defined(MAIN_PASS)
    {
        LineDetectionOutput lo = get_line_detection();

        float line = any(lo.id_boundary) ? id_boundary_width : 0.0;
        
        if(lo.delta_distance > min_depth_threshold)
        {
            float depth = map_range_clamped(
                lo.delta_distance, 
                min_depth_threshold, max_depth_threshold,
                min_depth_width, max_depth_width
            );

            line = max(line, depth);
        }
        if(lo.delta_angle > min_angle_threshold)
        {
            float angle = map_range_clamped(
                lo.delta_angle, 
                min_angle_threshold, max_angle_threshold,
                min_angle_width, max_angle_width
            );

            line = max(line, angle);
        }

        return line;
        
    }
    #else
    {
        return 0.0;
    }
    #endif
}

vec4 get_random_vector(float seed)
{
    #ifdef PIXEL_SHADER
    {
        return random_vector(random_per_pixel, seed);
    }
    #else
    {
        return random_vector(random_per_sample, seed);
    }
    #endif
}

float get_random(float seed)
{
    return get_random_vector(seed).x;
}

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

