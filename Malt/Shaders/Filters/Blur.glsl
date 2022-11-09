#ifndef BLUR_GLSL
#define BLUR_GLSL

/*  META GLOBAL
    @meta: category=Filter; subcategory=Blur;
*/

/*  META
    @input_texture: label=Texture;
    @uv: label=UV; default=UV[0];
    @radius: default=5.0; min=0.0;
*/
vec4 box_blur(sampler2D input_texture, vec2 uv, float radius, bool circular)
{
    if(radius <= 1.0)
    {
        return texture(input_texture, uv);
    }
    vec2 resolution = textureSize(input_texture, 0);

    vec4 result = vec4(0);
    float total_weight = 0.0;

    for(float x = -radius; x <= radius; x++)
    {
        for(float y = -radius; y <= radius; y++)
        {
            vec2 offset = vec2(x,y);
            if(!circular || length(offset) <= radius)
            {
                result += texture(input_texture, uv + offset / resolution);
                total_weight += 1.0;
            }
        }   
    }

    return result / total_weight;
}

float _gaussian_weight(float x, float sigma)
{
    float sigma2 = sigma * sigma;

    return (1.0 / sqrt(2*PI*sigma2)) * exp(-(x*x / 2.0*sigma2));
}

float _gaussian_weight_2d(vec2 v, float sigma)
{
    float sigma2 = sigma * sigma;

    return (1.0 / (2*PI*sigma2)) * exp(-(dot(v,v) / (2.0*sigma2)));
}

float _gaussian_weight_3d(vec3 v, float sigma)
{
	return 0.39894*exp(-0.5*dot(v,v)/(sigma*sigma))/sigma;
}

/*  META
    @input_texture: label=Texture;
    @uv: label=UV; default=UV[0];
    @radius: default=5.0; min=0.0;
    @sigma: default=1.0;
*/
vec4 gaussian_blur(sampler2D input_texture, vec2 uv, float radius, float sigma)
{
    if(radius <= 1.0 || sigma <= 0.0)
    {
        return texture(input_texture, uv);
    }
    vec2 resolution = textureSize(input_texture, 0);

    vec4 result = vec4(0);
    float total_weight = 0.0;

    for(float x = -radius; x <= radius; x++)
    {
        for(float y = -radius; y <= radius; y++)
        {
            vec2 offset = vec2(x,y);
            float weight = _gaussian_weight_2d(offset, sigma);
            result += texture(input_texture, uv + offset / resolution) * weight;
            total_weight += weight;
        }   
    }

    return result / total_weight;
}

#include "Common/Math.glsl"

/*  META
    @input_texture: label=Texture;
    @uv: label=UV; default=UV[0];
    @radius: default=5.0;
    @distribution_exponent: default=5.0;
    @samples: default=8; min=1;
*/
vec4 jitter_blur(sampler2D input_texture, vec2 uv, float radius, float distribution_exponent, int samples)
{
    if(samples <= 0 || radius <= 0.0)
    {
        return texture(input_texture, uv);
    }
    vec2 resolution = textureSize(input_texture, 0);
    vec4 result = vec4(0);

    for(int i = 0; i < samples;  i++)
    {
        vec4 random = random_per_pixel(i);
        float angle = random.x * PI * 2;
        float length = random.y;
        length = pow(length, distribution_exponent) * radius;
        float x = cos(angle) * length;
        float y = sin(angle) * length;
        vec2 offset = vec2(x,y) / resolution;
        result += texture(input_texture, uv + offset) / samples;
    }

    return result;
}

/* META
    @meta: internal=true;
    @uv: default=UV[0];
*/
vec4 tent_blur(sampler2D tex, vec2 uv)
{
    // Half pixel offset takes advantage of hardware texture interpolation to achieve a 3x3 gaussian blur
    // with just 4 samples instead of 9.
    // The resulting kernel looks like this:
    //  1  2  1
    //  2  4  2
    //  1  2  1
    vec2 texel = 1.0 / textureSize(tex, 0);
    return
        (texture(tex, uv + texel * vec2(-0.5, -0.5)) +
         texture(tex, uv + texel * vec2(-0.5, +0.5)) +
         texture(tex, uv + texel * vec2(+0.5, -0.5)) +
         texture(tex, uv + texel * vec2(+0.5, +0.5))) / 4.0;
}

/* META
    @meta: label=Bilateral;
    @tex: label=Texture;
    @uv: label=UV; default=UV[0];
    @radius: default=5; min=0;
    @sigma: default=10.0; min=0.0;
    @bsigma: label=BSigma; default=0.1; min=0.0;

*/
vec4 bilateral_blur(sampler2D input_texture, vec2 uv, float radius, float sigma, float bsigma)
{

    // Similar to a gaussian blur but in addition to weighting the pixel distance it also weights the color difference.
    // Is good at preserving edges
    // Sigma -> controls pixel distance weight
    // BSigma -> controls color distance weight

    // https://people.csail.mit.edu/sparis/bf_course/course_notes.pdf

    vec2 texel = 1.0 / textureSize(input_texture, 0);

    float total_weight = 0.0;
    vec3 total_color = vec3(0.0);
    vec4 main_color = texture(input_texture, uv);

    if(radius <= 0.0 || sigma <= 0.0 || bsigma <= 0.0)
    {
        return main_color;
    }

    for(float u = -radius; u <= radius; u ++)
    {
        for(float v = -radius; v <= radius; v++)
        {
            vec2 o = vec2(u,v);
            vec3 color = texture(input_texture, uv + o * texel).rgb;

            float dist_weight = _gaussian_weight_2d(o, sigma);
            float diff_weight = _gaussian_weight_3d(color - main_color.rgb, bsigma);
            float weight = dist_weight * diff_weight;

            total_weight += weight;
            total_color += weight * color;
        }
    }
    return vec4(total_color / total_weight, main_color.a);

}

/* META
    @meta: label=Orientation-Aligned Bilateral;
    @tex: label=Texture;
    @uv: label=UV; default=UV[0];
    @flow: default='vec2(0)';
    @radius: default=6.0; min=0.0;
    @smoothness: default=0.55; min=0.0;
*/
vec4 OAB_blur(sampler2D input_texture, vec2 uv, vec2 flow, float radius, float smoothness)
{
    // Orientation-aligned Bilateral Blur
    // Smoothes image while preserving edges by using the local structure of the texture

    if(radius <= 0.0 || smoothness <= 0.0)
    {
        return texture(input_texture, uv);
    }
    float D = 2 * radius * radius;
    float R = 2 * smoothness * smoothness;

    vec2 dir = flow;
    vec2 dir_abs = abs(dir);
    float d_max = 1.0 / max(dir_abs.x, dir_abs.y);
    dir *= 1.0 / textureSize(input_texture, 0);

    vec4 main_color = texture(input_texture, uv);
    vec3 total_color = main_color.rgb;
    float total_weight = 1.0;
    float half_width = 2.0 * radius;
    for(float d = -half_width; d <= half_width; d += d_max)
    {
        vec3 color = texture(input_texture, uv + d * dir).rgb;
        float difference = length(color - main_color.rgb);
        float dist_influence = exp(-d * d / D);
        float diff_influence = exp(-difference * difference / R);
        float local_weight = dist_influence * diff_influence;
        total_weight += local_weight;
        total_color += local_weight * color;
    }
    return vec4(total_color / total_weight, main_color.a);
}

#endif //BLUR_GLSL
