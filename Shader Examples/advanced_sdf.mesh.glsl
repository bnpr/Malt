//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "NPR_Pipeline.glsl"

#include "SDF/SDF.glsl"

uniform int max_steps = 64;
uniform float min_precision = 0.0001;
uniform bool debug_steps = false;
uniform sampler1D debug_ramp;

uniform int particles = 30;
uniform float particle_radius = 0.1;
uniform float blend_size = 0.1;
uniform float time_scale = 1.0;

// scene_sdf always must be declared to use SDF.glsl
float scene_sdf(vec3 p)
{
    float result;

    vec3 top = vec3(0,0,5);
    float a = sdf_sphere(p, 1.0);
    float b = sdf_sphere(p - top, 1.0);

    result = sdf_union(a, b);

    for(int i = 0;  i < particles; i++)
    {
        vec3 location = random_vector(random_base, vec2(i, 0)).xyz;
        location.xy -= vec2(0.5);

        location.z = mod(TIME * time_scale * location.z, top.z);

        result = sdf_union_smooth(result, sdf_sphere(p - location, particle_radius), blend_size);
    }

    return result;
}

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec3 ray_origin = transform_point(inverse(CAMERA), screen_to_camera(screen_uv(), 0));
    vec3 ray_end = transform_point(inverse(CAMERA), screen_to_camera(screen_uv(), 1));
    RayMarchResult r = raymarch_scene(ray_origin, ray_end, max_steps, min_precision);

    #ifdef PIXEL_SHADER
    {
        if(r.hit)
        {
            // Set custom pixel depth, so shadow maps and depth testing behave correctly
            float projected_depth = project_point(PROJECTION * CAMERA, r.position).z;
            float far = gl_DepthRange.far;
            float near = gl_DepthRange.near;
            gl_FragDepth = (((far-near) * projected_depth) + near + far) / 2.0;
        }
    }
    #endif
    
    for(int i = 0; i < 4; i++)
    {
        PO.color.rgb += scene_diffuse_half(r.position, r.normal, MATERIAL_LIGHT_GROUPS[i], Settings.Receive_Shadow, Settings.Self_Shadow);
    }
    PO.color.a = r.hit ? 1.0 : 0.0;
    PO.normal = r.normal;

    if(debug_steps)
    {
        PO.color = texture(debug_ramp, float(r.step) / float(max_steps));
    }
}

