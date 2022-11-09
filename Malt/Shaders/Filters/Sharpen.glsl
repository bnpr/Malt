#ifndef SHARPEN_GLSL
#define SHARPEN_GLSL

#include "Filters/Blur.glsl"

/*  META GLOBAL
    @meta: category=Filter; subcategory=Sharpen;
*/

vec4 _sharpen_common(sampler2D tex, vec2 uv, vec4 blurred, float sharpness)
{
    vec4 base = texture(tex, uv);
    float scaler = 10.0; // Use scalar to put the range of the sharpness value mostly between 0-1 for convenience
    return base + (base - blurred) * sharpness * scaler;
}

/* META
    @meta: label=Box;
    @tex: label=Texture;
    @uv: label=UV; default = UV[0];
    @radius: default=1.0; min=0.0;
    @sharpness: default = 0.3; min=0.0;
*/
vec4 box_sharpen(sampler2D tex, vec2 uv, float radius, bool circular, float sharpness)
{
    vec4 blurred = box_blur(tex, uv, radius, circular);
    return _sharpen_common(tex, uv, blurred, sharpness);
}

/* META
    @meta: label=Gaussian;
    @tex: label=Texture;
    @uv: label=UV; default = UV[0];
    @radius: default=1.0; min=0.0;
    @sigma: default=1.0;
    @sharpness: default = 0.3; min=0.0;
*/
vec4 gaussian_sharpen(sampler2D tex, vec2 uv, float radius, float sigma, float sharpness)
{
    vec4 blurred = gaussian_blur(tex, uv, radius, sigma);
    return _sharpen_common(tex, uv, blurred, sharpness);
}

/* META
    @meta: label=Jitter;
    @tex: label=Texture;
    @uv: label=UV; default = UV[0];
    @radius: default=1.0; min=0.0;
    @distribution_exponent: default=5.0;
    @samples: default=8; min=1;
    @sharpness: default = 0.3; min=0.0;
*/
vec4 jitter_sharpen(sampler2D tex, vec2 uv, float radius, float distribution_exponent, int samples, float sharpness)
{
    vec4 blurred = jitter_blur(tex, uv, radius, distribution_exponent, samples);
    return _sharpen_common(tex, uv, blurred, sharpness);
}


#endif //SHARPEN_GLSL
