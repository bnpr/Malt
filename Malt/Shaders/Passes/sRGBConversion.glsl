#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    DEFAULT_SCREEN_VERTEX_SHADER();
}
#endif

#ifdef PIXEL_SHADER

uniform sampler2D input_texture;
uniform bool to_srgb;
uniform bool convert = true;

layout (location = 0) out vec4 OUT_COLOR;

void main()
{
    PIXEL_SETUP_INPUT();

    vec4 color = texture(input_texture, UV[0]);
    if(convert)
    {
        if(to_srgb)
        {
            color.rgb = linear_to_srgb(color.rgb);
        }
        else
        {
            color.rgb = srgb_to_linear(color.rgb);
        }
    }
    OUT_COLOR = color;
}

#endif //PIXEL_SHADER
