#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    DEFAULT_SCREEN_VERTEX_SHADER();
}
#endif

#ifdef PIXEL_SHADER

uniform sampler2D blend_texture;

layout (location = 0) out vec4 OUT_COLOR;

void main()
{
    PIXEL_SETUP_INPUT();

    vec4 color = texture(blend_texture, UV[0]);
    color.rgb *= color.a;
    OUT_COLOR = color;
}

#endif //PIXEL_SHADER
