#include "Shading/DiffuseGradient.glsl"
#include "Shading/SpecularGradient.glsl"

uniform sampler1D diffuse_gradient;
uniform sampler1D specular_gradient;
uniform float shininess = 1.0;


MAIN_PASS
{
    vec3 normal = normalize(NORMAL);

    vec3 color = diffuse_gradient_bsdf(POSITION, normal, diffuse_gradient);
    color += specular_gradient_bsdf(POSITION, normal, shininess, specular_gradient);

    OUT_COLOR = vec4(color, 1.0);
}