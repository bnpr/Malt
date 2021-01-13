//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    POSITION = in_position;
    UV[0] = in_position.xy * 0.5 + 0.5;

    gl_Position = vec4(POSITION, 1);
}
#endif

#ifdef PIXEL_SHADER

#include "Filters/AO.glsl"

uniform sampler2D IN_NORMAL_DEPTH;
uniform int samples = 16;
uniform float radius = 0.75;

layout (location = 0) out vec4 OUT_RESULT;

void main()
{
    float depth = texture(IN_NORMAL_DEPTH, UV[0]).w;
    vec3 position = screen_to_camera(UV[0], depth);
    position = transform_point(inverse(CAMERA), position);
    vec3 normal = texture(IN_NORMAL_DEPTH, UV[0]).xyz;

    float ao = ao_ex(IN_NORMAL_DEPTH, 3, position, normal, samples, radius, 5.0, 0);
    ao = pow(ao, 5.0); //Pow for more contrast
    //TODO: For some reason, using pow causes some values to go below 0 ?!?!?!?
    ao = max(0, ao);
    OUT_RESULT.r = ao;
}

#endif //PIXEL_SHADER
