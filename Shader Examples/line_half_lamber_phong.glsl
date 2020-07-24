#include "Shading/Lambert.glsl"
#include "Shading/Phong.glsl"
#include "Filters/Line.glsl"

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform vec3 diffuse_color = vec3(0.5,0.5,0.5);
uniform vec3 line_color;
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float shininess = 32.0;
uniform float line_width = 1.0;
uniform int line_steps = 1;
uniform float line_normal_threshold = 1.0;
uniform float line_depth_threshold = 0.5;

MAIN_PASS
{
    vec3 normal = normalize(NORMAL);
    
    vec3 diffuse = diffuse_color * half_lambert_bsdf(POSITION, normal);
    vec3 specular = specular_color * phong_bsdf(POSITION, normal, shininess);
    vec3 color = ambient_color + diffuse + specular;

    LineOutput lo = line_ex(
        line_width,
        line_steps,
        LINE_DEPTH_MODE_NEAR,
        screen_uv(),
        IN_NORMAL_DEPTH,
        3,
        IN_NORMAL_DEPTH,
        IN_ID,
        0
    );

    bool line = lo.id_boundary || 
                lo.delta_angle > line_normal_threshold || 
                lo.delta_distance > line_depth_threshold;
    
    vec3 result = mix(color, line_color, float(line));
    OUT_COLOR = vec4(result, 1.0);
}