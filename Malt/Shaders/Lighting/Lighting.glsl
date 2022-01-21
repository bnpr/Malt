#ifndef COMMON_LIGHTING_GLSL
#define COMMON_LIGHTING_GLSL

#include "Common.glsl"

#ifndef MAX_LIGHTS
    #define MAX_LIGHTS 128
#endif

#define LIGHT_SUN 1
#define LIGHT_POINT 2
#define LIGHT_SPOT 3

struct Light
{
    vec3 color;
    int type;
    vec3 position;
    float radius;
    vec3 direction;
    float spot_angle;
    float spot_blend;
    int type_index;
};

#define MAX_SPOTS 64
#define MAX_SUNS 64
#define MAX_POINTS 64

struct SceneLights
{
    Light lights[MAX_LIGHTS];
    int lights_count;
    int cascades_count;
    mat4 spot_matrices[MAX_SPOTS];
    mat4 sun_matrices[MAX_SUNS];
    mat4 point_matrices[MAX_POINTS];
};

layout(std140) uniform SCENE_LIGHTS
{
    SceneLights LIGHTS;
};

uniform sampler2DArray SHADOWMAPS_DEPTH_SPOT;
uniform sampler2DArray SHADOWMAPS_DEPTH_SUN;
uniform samplerCubeArray SHADOWMAPS_DEPTH_POINT;

struct LitSurface
{
    vec3 N;// Surface normal
    vec3 L;// Surface to light direction (normalized)
    vec3 V;// Surface to camera (view) direction (normalized)
    vec3 R;// -L reflected on N
    vec3 H;// Halfway vector
    float NoL;// Dot product between N and L
    float P;// Power Scalar
    bool shadow;
    int cascade;
    vec3 shadow_multiply;
    vec3 light_color;
};

struct ShadowData
{
    vec3 light_uv;
    bool shadow;
    vec3 light_space;
    float depth;
};

ShadowData spot_shadow(vec3 position, Light light, sampler2DArray shadowmap, float bias);
ShadowData sun_shadow(vec3 position, Light light, sampler2DArray shadowmap, float bias, out int cascade);
ShadowData point_shadow(vec3 position, Light light, samplerCubeArray shadowmap, float bias);

/*  META
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
*/
LitSurface lit_surface(vec3 position, vec3 normal, Light light, bool shadows)
{
    LitSurface S;

    S.N = normal;
    
    if (light.type == LIGHT_SUN)
    {
        S.L = -light.direction;
    }
    else
    {
        S.L = normalize(light.position - position);
    }

    S.V = view_direction();
    S.R = reflect(-S.L, S.N);
    S.H = normalize(S.L + S.V);
    S.NoL = dot(S.N,S.L);

    S.P = 1.0;

    if (light.type != LIGHT_SUN) //Point or Spot
    {
        float normalized_distance = distance(position, light.position) / light.radius;
        normalized_distance = clamp(normalized_distance, 0, 1);

        S.P = 1.0 - normalized_distance;
    }
    
    if (light.type == LIGHT_SPOT)
    {
        float spot_angle = dot(light.direction, normalize(position - light.position));
        spot_angle = acos(spot_angle);

        float end_angle = light.spot_angle / 2.0;
        float start_angle = end_angle - light.spot_blend;
        float delta_angle = end_angle - start_angle;
        
        float spot_scalar = clamp((spot_angle - start_angle) / delta_angle, 0, 1);

        S.P *= 1.0 - spot_scalar;
    }

    S.shadow = false;
    S.cascade = -1;
    
    if(shadows)
    {

        if(light.type_index >= 0)
        {
            float bias = 1e-5;
            if(light.type == LIGHT_SPOT)
            {
                S.shadow = spot_shadow(position, light, SHADOWMAPS_DEPTH_SPOT, bias).shadow;
            }
            if(light.type == LIGHT_SUN)
            {
                float bias = 1e-3;
                //bias *= 1.0 - abs(S.NoL);
                S.shadow = sun_shadow(position, light, SHADOWMAPS_DEPTH_SUN, bias, S.cascade).shadow;
            }
            if(light.type == LIGHT_POINT)
            {
                S.shadow = point_shadow(position, light, SHADOWMAPS_DEPTH_POINT, bias).shadow;
            }
        }
    }

    S.shadow_multiply = S.shadow ? vec3(0) : vec3(1);
    S.light_color = light.color * S.P * S.shadow_multiply;

    return S;
}

ShadowData spot_shadow(vec3 position, Light light, sampler2DArray shadowmap, float bias)
{
    vec2 shadowmap_size = vec2(textureSize(shadowmap, 0));
    
    ShadowData S;
    S.light_space = project_point(LIGHTS.spot_matrices[light.type_index], position);
    S.light_space.xy += (SAMPLE_OFFSET / shadowmap_size);    
    
    S.light_uv = S.light_space * 0.5 + 0.5;
    S.depth = texture(shadowmap, vec3(S.light_uv.xy, light.type_index)).x;

    S.shadow = S.depth < S.light_uv.z - bias && S.light_uv == clamp(S.light_uv, vec3(0), vec3(1));
    //if(!S.shadow) S.depth = 0;

    return S;
}

ShadowData sun_shadow(vec3 position, Light light, sampler2DArray shadowmap, float bias, out int cascade)
{
    vec2 shadowmap_size = vec2(textureSize(shadowmap, 0));
    
    ShadowData S;
    S.shadow = false;

    for(int c = 0; c < LIGHTS.cascades_count; c++)
    {
        int index = light.type_index * LIGHTS.cascades_count + c;
        
        S.light_space = project_point(LIGHTS.sun_matrices[index], position);
        S.light_space.xy += (SAMPLE_OFFSET / shadowmap_size);
        
        S.light_uv = S.light_space * 0.5 + 0.5;

        if(S.light_space == clamp(S.light_space, vec3(-1), vec3(1)))
        {
            S.depth = texture(shadowmap, vec3(S.light_uv.xy, index)).x;
            S.shadow = S.depth < S.light_uv.z - bias;

            cascade = c;
            break;
        }
    }

    return S;
}

ShadowData point_shadow(vec3 position, Light light, samplerCubeArray shadowmap, float bias)
{
    vec2 shadowmap_size = vec2(textureSize(shadowmap, 0));
    
    ShadowData S;
    S.light_space = transform_point(LIGHTS.point_matrices[light.type_index], position);
    S.light_uv = normalize(S.light_space);
    
    float cubemap_side_depth = max(abs(S.light_space.x), max(abs(S.light_space.y), abs(S.light_space.z)));
    float n = 0.01; //Near is hard-coded for point lights
    float f = light.radius;
    float buffer_depth = (f+n) / (f-n) - (2*f*n)/(f-n) / cubemap_side_depth;
    buffer_depth = (buffer_depth + 1.0) * 0.5;

    S.depth = texture(shadowmap, vec4(S.light_uv, light.type_index)).x;
    
    S.shadow = S.depth < buffer_depth - bias;
    if(!S.shadow) S.depth = 0;

    return S;
}

#endif //COMMON_LIGHTING_GLSL

