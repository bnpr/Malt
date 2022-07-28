#include "NPR_Intellisense.glsl"
#include "Common.glsl"

/* META GLOBAL
    @meta: internal=true; 
*/
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
#ifdef CUSTOM_DEPTH_OFFSET
void DEPTH_OFFSET(inout float depth_offset, inout bool offset_position);
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

    float depth = gl_FragCoord.z;
    vec3 offset_position = POSITION;

    // Discard pixel at the end of the shader, to avoid derivative glitches.
    bool discard_pixel = false;
    
    #ifdef CUSTOM_PRE_PASS
    {
        PRE_PASS_PIXEL_SHADER(PPO);

        if(PPO.opacity <= 0)
        {
            discard_pixel = true;
        }
        else if(!Settings.Transparency)
        {
            PPO.opacity = 1.0;
        }
    }
    #endif

    #ifdef CUSTOM_DEPTH_OFFSET
    {
        float depth_offset = 0;
        bool offset_position = false;
        DEPTH_OFFSET(depth_offset, offset_position);
        
        #ifdef SHADOW_PASS
        {
            if(!offset_position) depth_offset = 0;
        }
        #endif
        
        vec3 position = POSITION + view_direction() * depth_offset;

        depth = project_point_to_screen_coordinates(PROJECTION * CAMERA, position).z;
        gl_FragDepth = depth;

        if(offset_position) POSITION = position;
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
                discard_pixel = true;
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
                discard_pixel = true;
            }

            if(Settings.Transparency_Single_Layer)
            {
                if(PPO.id.r == texelFetch(IN_LAST_ID, ivec2(gl_FragCoord.xy), 0).x)
                {
                    discard_pixel = true;
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
        NORMAL = texelFetch(IN_NORMAL_DEPTH, ivec2(gl_FragCoord.xy), 0).xyz;
        ID = texelFetch(IN_ID, ivec2(gl_FragCoord.xy), 0);
        MAIN_PASS_PIXEL_SHADER();
    }
    #endif

    if(discard_pixel)
    {
        discard;
    }
}

#endif //NDEF CUSTOM_MAIN

#endif //PIXEL_SHADER

#include "NPR_Pipeline/NPR_Mesh.glsl"
#include "NPR_Pipeline/NPR_Shading2.glsl"
