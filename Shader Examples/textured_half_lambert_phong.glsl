#include "Shading/Lambert.glsl"
#include "Shading/Phong.glsl"

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform sampler2D diffuse_color;
uniform int uv_index = 0;
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float shininess = 32.0;


MAIN_PASS
{
    vec3 normal = normalize(NORMAL);
    
    vec3 diffuse = texture(diffuse_color, UV[uv_index]).rgb * half_lambert_bsdf(POSITION, normal);
    vec3 specular = specular_color * phong_bsdf(POSITION, normal, shininess);
    vec3 color = ambient_color + diffuse + specular;

    OUT_COLOR = vec4(color, 1.0);
}