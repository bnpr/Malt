#include "NPR_Intellisense.glsl"

#ifdef PIXEL_SHADER
vec3 DEFERRED_TRUE_NORMAL;
#define CUSTOM_TRUE_NORMAL DEFERRED_TRUE_NORMAL
#endif

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
uniform bool DEFERRED_MODE = false;

void SCREEN_SHADER();

void main()
{
    PIXEL_SETUP_INPUT();
    
    DEFERRED_TRUE_NORMAL = reconstruct_normal(IN_NORMAL_DEPTH, 3, screen_pixel());

    if(RENDER_LAYER_MODE)
    {
        vec4 normal_depth =  texture(IN_NORMAL_DEPTH, UV[0]);
        if(DEFERRED_MODE && normal_depth.w == 1.0)
        {
            discard;
        }
        POSITION = screen_to_camera(UV[0], normal_depth.w);
        POSITION = transform_point(inverse(CAMERA), POSITION);
        NORMAL = normal_depth.xyz;
        ID = texture(IN_ID, UV[0]);
    }

    SCREEN_SHADER();
}
#endif

#include "NPR_Pipeline/NPR_Filters.glsl"
#include "NPR_Pipeline/NPR_Shading.glsl"
#include "NPR_Pipeline/NPR_Shading2.glsl"
