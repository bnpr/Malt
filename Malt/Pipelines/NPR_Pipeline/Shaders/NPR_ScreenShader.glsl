#include "NPR_Intellisense.glsl"
#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    DEFAULT_SCREEN_VERTEX_SHADER();
}
#endif

#ifdef PIXEL_SHADER
uniform sampler2D IN_NORMAL_DEPTH;
uniform usampler2D IN_ID;

uniform bool RENDER_LAYER_MODE = false;

void SCREEN_SHADER();

void main()
{
    PIXEL_SETUP_INPUT();
    
    vec4 normal_depth =  texture(IN_NORMAL_DEPTH, UV[0]);
    if(RENDER_LAYER_MODE && normal_depth.w == 1.0)
    {
        discard;
    }
    POSITION = screen_to_camera(UV[0], normal_depth.w);
    POSITION = transform_point(inverse(CAMERA), POSITION);
    NORMAL = normal_depth.xyz;
    ID = texture(IN_ID, UV[0]);

    SCREEN_SHADER();
}
#endif

#include "NPR_Pipeline/NPR_Filters.glsl"
#include "NPR_Pipeline/NPR_Shading.glsl"
