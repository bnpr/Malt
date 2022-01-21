#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    DEFAULT_SCREEN_VERTEX_SHADER();
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
