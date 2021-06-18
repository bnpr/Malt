//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

/// NPR Pipeline for mesh materials.
/// Includes a simplified API for writing shaders.

#include "Common.glsl"

// All the mesh surface data of the currently shaded pixel.
struct Surface
{
    vec3 position;// Surface position
    vec3 normal;// Surface normal
    vec3 tangent[4];// Surface tangents, one for each UV. Only available if use_precomputed normals is enabled in the mesh settings panel.
    vec3 bitangent[4];
    vec2 uv[4];
    vec4 color[4]; // Vertex colors. Black if unused.
    float id;
};

// The result of the pixel shader.
struct PixelOutput
{
    vec4 color;
    vec3 normal;
    float id;
    vec4 line_color;
    float line_width;
    vec4 shadow_color; // Only for transparent objects
};

// Global material settings. Can be modified in the material panel UI
struct NPR_Settings
{
    bool Self_Shadow;
    bool Transparency;
    bool Transparency_Single_Layer;
    float Vertex_Displacement_Offset;
};

uniform NPR_Settings Settings = NPR_Settings(true, false, false, 0.001);

#ifdef VERTEX_SHADER

void COMMON_VERTEX_SHADER(inout Surface S);

#ifndef CUSTOM_VERTEX_SHADER
void COMMON_VERTEX_SHADER(inout Surface S){}
#endif

vec3 VERTEX_DISPLACEMENT_SHADER(Surface S);

#ifndef CUSTOM_VERTEX_DISPLACEMENT
vec3 VERTEX_DISPLACEMENT_SHADER(Surface S){ return vec3(0); }
#endif

#ifndef VERTEX_DISPLACEMENT_OFFSET
    #define VERTEX_DISPLACEMENT_OFFSET 0.1
#endif

#ifndef CUSTOM_MAIN
void main()
{
    DEFAULT_VERTEX_SHADER();

    Surface S;
    S.position = POSITION;
    S.normal = NORMAL;
    S.tangent = TANGENT;
    S.bitangent = BITANGENT;
    S.uv = UV;
    S.color = COLOR;
    S.id = ID;
    
    COMMON_VERTEX_SHADER(S);

    POSITION = S.position;
    NORMAL = S.normal;
    TANGENT = S.tangent;
    BITANGENT = S.bitangent;
    UV = S.uv;
    COLOR = S.color;
    //ID = S.ID TODO???

    #ifdef CUSTOM_VERTEX_DISPLACEMENT
    {
        vec3 displaced_position = POSITION + VERTEX_DISPLACEMENT_SHADER(S);
        for(int i = 0; i < TANGENT.length(); i++)
        {
            Surface s = S;

            s.position = POSITION + TANGENT[i] * Settings.Vertex_Displacement_Offset;
            vec3 displaced_tangent = s.position + VERTEX_DISPLACEMENT_SHADER(s);
            TANGENT[i] = normalize(displaced_tangent - displaced_position);

            s.position = POSITION + BITANGENT[i] * Settings.Vertex_Displacement_Offset;
            vec3 displaced_bitangent = s.position + VERTEX_DISPLACEMENT_SHADER(s);
            BITANGENT[i] = normalize(displaced_bitangent - displaced_position);
        }
        POSITION = displaced_position;
        NORMAL = normalize(cross(TANGENT[0], BITANGENT[0]));
    }
    #endif
    
    VERTEX_SETUP_OUTPUT();
}
#endif //NDEF CUSTOM_MAIN

#endif //VERTEX_SHADER

#ifdef PIXEL_SHADER

uniform sampler2D IN_OPAQUE_DEPTH;
uniform sampler2D IN_TRANSPARENT_DEPTH;
uniform sampler2D IN_LAST_ID;

#ifdef SHADOW_PASS
layout (location = 0) out float OUT_ID;
layout (location = 1) out vec3 OUT_SHADOW_COLOR;
#endif //PRE_PASS

#ifdef PRE_PASS
layout (location = 0) out vec4 OUT_NORMAL_DEPTH;
layout (location = 1) out float OUT_ID;
#endif //PRE_PASS

#ifdef MAIN_PASS
uniform sampler2D IN_NORMAL_DEPTH;
uniform sampler2D IN_ID;

layout (location = 0) out vec4 OUT_COLOR;
layout (location = 1) out vec4 OUT_LINE_COLOR;
layout (location = 2) out vec4 OUT_LINE_DATA;
#endif //MAIN_PASS

#ifndef CUSTOM_MAIN

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO);

void main()
{
    Surface S;
    S.position = POSITION;
    S.normal = normalize(NORMAL) * (gl_FrontFacing ? 1.0 : -1.0);
    S.tangent = TANGENT;
    S.bitangent = BITANGENT;
    S.uv = UV;
    S.color = COLOR;
    S.id = ID;

    PixelOutput PO;
    PO.color = vec4(0,0,0,1);
    PO.normal = S.normal;
    PO.id = ID;
    PO.line_color = vec4(0,0,0,1);
    PO.line_width = 0;

    if(Settings.Transparency)
    {
        #ifndef SHADOW_PASS
        {
            float opaque_depth = texelFetch(IN_OPAQUE_DEPTH, ivec2(gl_FragCoord.xy), 0).x;
            float transparent_depth = texelFetch(IN_TRANSPARENT_DEPTH, ivec2(gl_FragCoord.xy), 0).x;
            float depth = (gl_FragCoord.z / gl_FragCoord.w) * 0.5 + 0.5;
            depth = gl_FragCoord.z;
            
            if(depth >= opaque_depth || depth <= transparent_depth)
            {
                discard;
            }
        }
        #endif
    }

    COMMON_PIXEL_SHADER(S, PO);

    if(PO.color.a <= 0)
    {
        discard;
    }

    {
    if(Settings.Transparency && Settings.Transparency_Single_Layer)
        if(round(PO.id) == round(texelFetch(IN_LAST_ID, ivec2(gl_FragCoord.xy), 0).x))
        {
            discard;
        }
    }

    #ifdef SHADOW_PASS
    {
        OUT_ID = PO.id;

        if(Settings.Transparency)
        {
            OUT_SHADOW_COLOR = PO.shadow_color.rgb;

            float a = random_per_pixel(transform_point(CAMERA, POSITION).z);
            float b = random_per_sample(PO.id);
            float c = random_per_sample(transform_point(CAMERA, POSITION).z);
            float pass_through = c;
            if(pass_through > PO.shadow_color.a)
            {
                discard;
            }
        }
    }
    #endif

    #ifdef PRE_PASS
    {
        OUT_NORMAL_DEPTH.xyz = PO.normal;
        OUT_NORMAL_DEPTH.w = gl_FragCoord.z;
        OUT_ID = PO.id;
    }
    #endif

    #ifdef MAIN_PASS
    {
        OUT_COLOR = PO.color;
        if(PO.line_width > 0 && PO.line_color.a > 0)
        {
            OUT_LINE_COLOR = PO.line_color;
            OUT_LINE_DATA.xy = screen_uv();
            OUT_LINE_DATA.z = PO.line_width;
        }
    }
    #endif
}
#endif //NDEF CUSTOM_MAIN

#endif //PIXEL_SHADER

//NPR PIPELINE SIMPLIFIED API

#include "NPR_Shading.glsl"
#include "Shading/Rim.glsl"
#include "Filters/AO.glsl"
#include "Filters/Curvature.glsl"
#include "Filters/Line.glsl"


// Normal of the currently shaded pixel surface.
// Returns the PixelOutput normal in the Main Pass and the smooth mesh normal in other passes
vec3 get_normal()
{
    #if defined(PIXEL_SHADER) && defined(MAIN_PASS)
    {
        return texelFetch(IN_NORMAL_DEPTH, ivec2(gl_FragCoord.xy), 0).xyz;
    }
    #endif
    return normalize(NORMAL);
}

vec3 get_diffuse()
{
    return scene_diffuse(POSITION, get_normal());
}

vec3 get_diffuse_half()
{
    return scene_diffuse_half(POSITION, get_normal());
}

vec3 get_diffuse_gradient(sampler1D gradient_texture)
{
    return scene_diffuse_gradient(POSITION, get_normal(), gradient_texture);
}

vec3 get_specular(float roughness)
{
    return scene_specular(POSITION, get_normal(), roughness);
}

vec3 get_specular_gradient(sampler1D gradient_texture, float roughness)
{
    return scene_specular_gradient(POSITION, get_normal(), roughness, gradient_texture);
}

vec3 get_specular_anisotropic(float roughness, float anisotropy, vec3 tangent)
{
    return scene_specular_anisotropic(POSITION, get_normal(), tangent, anisotropy, roughness);
}

vec3 get_specular_anisotropic_gradient(sampler1D gradient_texture, float roughness, float anisotropy, vec3 tangent)
{
    return scene_specular_anisotropic_gradient(POSITION, get_normal(), tangent, anisotropy, roughness, gradient_texture);
}

vec3 get_toon(float size, float gradient_size, float specularity, float offset)
{
    return scene_toon(POSITION, get_normal(), size, gradient_size, specularity, offset);
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

//TODO: World Space width for curvature

float get_line_simple(float width, float depth_threshold, float normal_threshold)
{
    #if defined(PIXEL_SHADER) && defined(MAIN_PASS)
    {
        LineOutput lo = line_ex(
            POSITION,
            get_normal(),
            1,
            1,
            LINE_DEPTH_MODE_NEAR,
            screen_uv(),
            IN_NORMAL_DEPTH,
            3,
            IN_NORMAL_DEPTH,
            IN_ID,
            0
        );

        bool line = lo.id_boundary || 
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
        LineOutput lo = line_ex(
            POSITION,
            get_normal(),
            1.0,
            1,
            LINE_DEPTH_MODE_NEAR,
            screen_uv(),
            IN_NORMAL_DEPTH,
            3,
            IN_NORMAL_DEPTH,
            IN_ID,
            0
        );

        float line = lo.id_boundary ? id_boundary_width : 0.0;
        
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


