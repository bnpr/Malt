//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform vec3 diffuse_color = vec3(1.0,0.1,0.1);
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float shininess = 32;

uniform vec3 line_color = vec3(0.0,0.0,0.0);
uniform float line_width_min = 1.0;
uniform float line_width_max = 3.0;
uniform float line_depth_threshold = 0.5;
uniform float line_normal_threshold = 1.0;

uniform bool line_use_id_boundary = false;
uniform float line_depth_min = 0.5;
uniform float line_depth_max = 2.0;
uniform float line_angle_min = 0.5;
uniform float line_angle_max = 1.5;


@MAIN_PASS_PIXEL_SHADER
{
    vec3 diffuse = diffuse_color * get_diffuse_half();
    vec3 specular = specular_color * get_specular(shininess);
    vec3 color = ambient_color + diffuse + specular;

    //Use 1 pixel line width when using OUT_LINE outputs, since line is expanded as a post-process
    float line = get_line_advanced(1.0, line_use_id_boundary, line_depth_min, line_depth_max, line_angle_min, line_angle_max);
    line *= line_width_max;

    if(line > 0.0)
    {
        OUT_LINE_COLOR = vec4(line_color, 1.0);
        OUT_LINE_DATA.xy = screen_uv();
        OUT_LINE_DATA.z = line;
    }

    color = mix(color, line_color, line);

    OUT_COLOR = vec4(color, 1.0);
}

