//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef COMMON_LIGHTING_GLSL
#define COMMON_LIGHTING_GLSL

#include "Common.glsl"
#include "Transform.glsl"

#ifndef MAX_LIGHTS
    #define MAX_LIGHTS 128
#endif

#define LIGHT_SUN 1
#define LIGHT_POINT 2
#define LIGHT_SPOT 3

struct Light
{
    mat4 matrix;
    vec3 color;
    int type;
    vec3 position;
    float radius;
    vec3 direction;
    float spot_angle;
    float spot_blend;
    int type_index;
};

struct SceneLights
{
    Light lights[MAX_LIGHTS];
    int lights_count;
};

uniform sampler2DArray SPOT_SHADOWMAPS;
uniform sampler2DArray SUN_SHADOWMAPS;
uniform samplerCubeArray POINT_SHADOWMAPS;

struct LitSurface
{
    vec3 N;// Surface normal
    vec3 L;// Surface to light direction (normalized)
    vec3 V;// Camera position to surface direction (normalized)
    vec3 R;// -L reflected on N
    vec3 H;// Halfway vector
    float NoL;// Dot product between N and L
    float P;// Power Scalar (Inverse attenuation)
    bool shadow;
};

LitSurface lit_surface(vec3 position, vec3 normal, Light light)
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

    //SHADOWS
    //TODO: Return shadow depth instead of bool ?
    bool shadowmaps = true;

    if(shadowmaps && light.type_index >= 0)
    {
        if(light.type == LIGHT_SPOT)
        {
            vec3 light_space = project_point(light.matrix, position);
            vec2 shadowmap_size = vec2(textureSize(SPOT_SHADOWMAPS, 0));
            light_space.xy += (SAMPLE_OFFSET / shadowmap_size);
            light_space = light_space * 0.5 + 0.5;
            vec2 light_uv = clamp(light_space.xy, vec2(0), vec2(1));
            
            float spot_space_depth = texture(SPOT_SHADOWMAPS, vec3(light_uv, light.type_index)).x;
            bool inside = abs(light_space.x) < 1 && abs(light_space.y) < 1 && light_space.z > 0 && light_space.z < 1;

            float bias = 1e-5;

            S.shadow = spot_space_depth < light_space.z - bias;
        }
    }

    return S;
}

#endif //COMMON_LIGHTING_GLSL

