//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    POSITION = in_position;
    UV[0] = in_position.xy * 0.5 + 0.5;
    
    VERTEX_SETUP_OUTPUT();

    gl_Position = vec4(POSITION, 1);
}
#endif

#ifdef PIXEL_SHADER

uniform sampler2D DEPTH_TEXTURE;
uniform int DEPTH_CHANNEL;

layout (location = 0) out vec4 OUT_RESULT;

void main()
{
    PIXEL_SETUP_INPUT();

    float depth = texture(DEPTH_TEXTURE, UV[0])[DEPTH_CHANNEL];
    vec3 camera = screen_to_camera(UV[0], depth);
    OUT_RESULT.r = -camera.z;
}

#endif //PIXEL_SHADER
