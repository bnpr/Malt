//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Pipelines/NPR_Pipeline.glsl"

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform vec3 diffuse_color = vec3(1.0,0.1,0.1);
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float roughness = 0.5;

uniform bool line_world_space = false;

uniform vec4 line_color = vec4(0.0,0.0,0.0,1.0);

uniform float line_id_boundary_width = 1.;

uniform float line_depth_threshold_min = 0.5;
uniform float line_depth_threshold_max = 2.0;
uniform float line_depth_width_min = 0.5;
uniform float line_depth_width_max = 2.0;

uniform float line_angle_threshold_min = 0.5;
uniform float line_angle_threshold_max = 1.5;
uniform float line_angle_width_min = 0.5;
uniform float line_angle_width_max = 2.0;


void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec3 diffuse = diffuse_color * get_diffuse_half();
    vec3 specular = specular_color * get_specular(roughness);
    vec3 color = ambient_color + diffuse + specular;

    float line = get_line_advanced(
        line_id_boundary_width,
        line_depth_threshold_min, line_depth_threshold_max, line_depth_width_min, line_depth_width_max,
        line_angle_threshold_min, line_angle_threshold_max, line_angle_width_min, line_angle_width_max);
    
    if(line_world_space)
    {
        line /= pixel_world_size_at(pixel_depth());
        // Here we divide by 100 just to make line size more consistent between modes,
        // but this is a completely optional hand-picked number
        line /= 100;
    }

    PO.color.rgb = color;
    PO.line_color = line_color;
    PO.line_width = line;
}

