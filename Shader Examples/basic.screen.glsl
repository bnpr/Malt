#include "NPR_Pipeline.glsl"

uniform sampler2D IN_COLOR;

uniform float Hue;
uniform float Saturation;
uniform float Value;

#ifdef PIXEL_SHADER
layout (location = 0) out vec4 OUT_RESULT;

void main()
{
    vec4 color = texture(IN_COLOR, UV[0]);

    vec3 hsv = rgb_to_hsv(color.rgb);
    hsv.x += Hue;
    hsv.y += Saturation;
    hsv.z += Value;
    hsv = clamp(hsv, vec3(0), vec3(1));

    OUT_RESULT.rgb = hsv_to_rgb(hsv);
    OUT_RESULT.a = color.a;
}
#endif

