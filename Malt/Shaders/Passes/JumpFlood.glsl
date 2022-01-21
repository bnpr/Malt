#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    DEFAULT_SCREEN_VERTEX_SHADER();
}
#endif

#ifdef PIXEL_SHADER

#include "Filters/JumpFlood.glsl"

uniform sampler2D input_texture;
uniform float width;

layout (location = 0) out vec4 OUT_RESULT;

void main()
{
    PIXEL_SETUP_INPUT();

    vec2 uv = screen_uv();
    OUT_RESULT = jump_flood(input_texture, uv, width, true);
}

#endif //PIXEL_SHADER
