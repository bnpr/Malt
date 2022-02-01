#include "NPR_Intellisense.glsl"
#include "Common.glsl"

/* META @meta: internal=true; */
struct NPR_Settings
{
    // Global material settings. Can be modified in the material panel UI
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
    vec4 color[4];
};

struct PrePassOutput
{
    vec3 normal;
    uvec4 id;
    float opacity;
    vec3 transparent_shadowmap_color;
    float depth_offset;
    bool offset_position;
};

#ifdef VERTEX_SHADER

void COMMON_VERTEX_SHADER(inout Vertex V);

#ifndef CUSTOM_VERTEX_SHADER
void COMMON_VERTEX_SHADER(inout Vertex V){}
#endif

vec3 VERTEX_DISPLACEMENT_SHADER();

vec3 VERTEX_DISPLACEMENT_WRAPPER(Vertex V)
{
    Vertex real;
    real.position = POSITION;
    real.tangent = TANGENT;
    real.bitangent = BITANGENT;

    POSITION = V.position;
    TANGENT = V.tangent;
    BITANGENT = V.bitangent;

    vec3 result = VERTEX_DISPLACEMENT_SHADER();

    POSITION = real.position;
    TANGENT = real.tangent;
    BITANGENT = real.bitangent;

    return result;
}

#ifndef CUSTOM_VERTEX_DISPLACEMENT
vec3 VERTEX_DISPLACEMENT_SHADER(){ return vec3(0); }
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
    V.id = ID;
    
    COMMON_VERTEX_SHADER(V);

    POSITION = V.position;
    NORMAL = V.normal;
    TANGENT = V.tangent;
    BITANGENT = V.bitangent;
    UV = V.uv;
    COLOR = V.color;
    ID = V.id;

    #ifdef CUSTOM_VERTEX_DISPLACEMENT
    {
        vec3 displaced_position = POSITION + VERTEX_DISPLACEMENT_WRAPPER(V);
        
        if(!PRECOMPUTED_TANGENTS)
        {
            vec3 axis = vec3(0,0,1);
            axis = abs(dot(axis, NORMAL)) < 0.99 ? axis : vec3(1,0,0);
            vec3 tangent = normalize(cross(axis, NORMAL));
            TANGENT = tangent;
            BITANGENT = normalize(cross(NORMAL, tangent));
        }
        
        Vertex v = V;

        v.position = POSITION + TANGENT * Settings.Vertex_Displacement_Offset;
        vec3 displaced_tangent = v.position + VERTEX_DISPLACEMENT_WRAPPER(v);
        TANGENT = normalize(displaced_tangent - displaced_position);

        v.position = POSITION + BITANGENT * Settings.Vertex_Displacement_Offset;
        vec3 displaced_bitangent = v.position + VERTEX_DISPLACEMENT_WRAPPER(v);
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

#ifdef SHADOW_PASS
layout (location = 0) out uint OUT_ID;
layout (location = 1) out vec3 OUT_SHADOW_MULTIPLY_COLOR;
#endif //PRE_PASS

#ifdef PRE_PASS
uniform sampler2D IN_OPAQUE_DEPTH;
uniform sampler2D IN_TRANSPARENT_DEPTH;
uniform usampler2D IN_LAST_ID;

layout (location = 0) out vec4 OUT_NORMAL_DEPTH;
layout (location = 1) out uvec4 OUT_ID;
#endif //PRE_PASS

#ifdef MAIN_PASS
uniform sampler2D IN_NORMAL_DEPTH;
uniform usampler2D IN_ID;
#endif //MAIN_PASS

#ifndef CUSTOM_MAIN

#ifdef CUSTOM_PRE_PASS
void PRE_PASS_PIXEL_SHADER(inout PrePassOutput PPO);
#endif
#ifdef MAIN_PASS
void MAIN_PASS_PIXEL_SHADER();
#endif

void main()
{
    PIXEL_SETUP_INPUT();

    PrePassOutput PPO;
    PPO.normal = NORMAL;
    PPO.id = ID;
    PPO.opacity = 1;
    PPO.transparent_shadowmap_color = vec3(0);
    PPO.depth_offset = 0;
    PPO.offset_position = true;

    float depth = gl_FragCoord.z;
    vec3 offset_position = POSITION;
    
    #ifdef CUSTOM_PRE_PASS
    {
        PRE_PASS_PIXEL_SHADER(PPO);

        if(PPO.opacity <= 0)
        {
            discard;
        }
        else if(!Settings.Transparency)
        {
            PPO.opacity = 1.0;
        }

        offset_position = POSITION + view_direction() * PPO.depth_offset;

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
    }
    #endif

    #ifdef SHADOW_PASS
    {
        OUT_ID = PPO.id.r;

        if(Settings.Transparency)
        {
            float pass_through = hash(vec2(ID.x, SAMPLE_COUNT)).x;
            if(pass_through > PPO.opacity)
            {
                discard;
            }
            OUT_SHADOW_MULTIPLY_COLOR = PPO.transparent_shadowmap_color;
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
                if(PPO.id.r == texelFetch(IN_LAST_ID, ivec2(gl_FragCoord.xy), 0).x)
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
        ID = texelFetch(IN_ID, ivec2(gl_FragCoord.xy), 0);

        MAIN_PASS_PIXEL_SHADER();
    }
    #endif
}

#endif //NDEF CUSTOM_MAIN

#endif //PIXEL_SHADER

#include "NPR_Pipeline/NPR_Filters.glsl"
#include "NPR_Pipeline/NPR_Shading.glsl"

vec3 diffuse_shading()
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += diffuse_shading(POSITION, NORMAL, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 diffuse_half_shading()
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += diffuse_half_shading(POSITION, NORMAL, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 diffuse_gradient_shading(sampler1D gradient_texture)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += diffuse_gradient_shading(POSITION, NORMAL, gradient_texture, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 specular_shading(float roughness)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += specular_shading(POSITION, NORMAL, roughness, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 specular_gradient_shading(sampler1D gradient_texture, float roughness)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += specular_gradient_shading(POSITION, NORMAL, roughness, gradient_texture, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

vec3 specular_anisotropic_shading(float roughness, float anisotropy, vec3 tangent)
{
    vec3 result = vec3(0);
    for(int i = 0; i < 4; i++)
    {
        result += specular_anisotropic_shading(POSITION, NORMAL, tangent, anisotropy, roughness, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    return result;
}

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

