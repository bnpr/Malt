#ifndef SHARPEN_GLSL
#define SHARPEN_GLSL

#include "Filters/Blur.glsl"

/* META
    @meta: category=Filter;
    @uv: default = UV[0];
    @sharpness: default = 0.3; min=0.0;
*/
vec4 sharpen(sampler2D tex, vec2 uv, float sharpness)
{
    vec4 base = texture(tex, uv);
    vec4 blurred_base = box_blur(tex, uv, 1, true);
    float scaler = 10.0; // Use scalar to put the range of the sharpness value mostly between 0-1 for convenience
    return base + (base - blurred_base) * sharpness * scaler;
}

#endif //SHARPEN_GLSL