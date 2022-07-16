#ifndef COMMON_COLOR_GLSL
#define COMMON_COLOR_GLSL

/*  META GLOBAL
    @meta: category=Color;
*/

/*  META
    @meta:doc=
    Blends the blend color as a layer over the base color.;
    @blend:default=vec4(0); doc=
    The blend color.;
*/
vec4 alpha_blend(vec4 base, vec4 blend)
{
    if(blend.a <= 0)
    {
        return base;
    }
    else if(blend.a >= 1)
    {
        return blend;
    }
    
    float alpha = blend.a + base.a * (1.0 - blend.a);
    vec4 result = (blend * blend.a + base * base.a * (1.0 - blend.a)) / alpha;
    result.a = alpha;

    return result;
}

float relative_luminance(vec3 color)
{
    return dot(color, vec3(0.2126,0.7152,0.0722));
}

float luma(vec3 color)
{
    return dot(color, vec3(0.299,0.587,0.114));
}

vec3 linear_to_srgb(vec3 linear)
{
    vec3 low = linear * 12.92;
    vec3 high = 1.055 * pow(linear, vec3(1.0/2.4)) - 0.055;
    return mix(low, high, greaterThan(linear, vec3(0.0031308)));
}

vec3 srgb_to_linear(vec3 srgb)
{
    vec3 low = srgb / 12.92;
    vec3 high = pow((srgb + 0.055)/1.055, vec3(2.4));
    return mix(low, high, greaterThan(srgb, vec3(0.04045)));
}

vec3 rgb_to_hsv(vec3 rgb)
{
    rgb = linear_to_srgb(rgb);
    //http://lolengine.net/blog/2013/07/27/rgb-to-hsv-in-glsl
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = rgb.g < rgb.b ? vec4(rgb.bg, K.wz) : vec4(rgb.gb, K.xy);
    vec4 q = rgb.r < p.x ? vec4(p.xyw, rgb.r) : vec4(rgb.r, p.yzx);

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

/*  META
    @hsv:subtype=HSV;
*/
vec3 hsv_to_rgb(vec3 hsv)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(hsv.xxx + K.xyz) * 6.0 - K.www);
    return srgb_to_linear(hsv.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), hsv.y));
}

vec4 hsv_edit(vec4 color, float hue, float saturation, float value)
{
    vec3 hsv = rgb_to_hsv(color.rgb);
    hsv += vec3(hue, saturation, value);
    return vec4(hsv_to_rgb(hsv), color.a);
}

vec3 rgb_gradient(sampler1D gradient, vec3 uvw)
{
    return vec3
    (
        texture(gradient, uvw.r).r,
        texture(gradient, uvw.g).g,
        texture(gradient, uvw.b).b
    );
}

vec4 rgba_gradient(sampler1D gradient, vec4 uvw)
{
    return vec4
    (
        texture(gradient, uvw.r).r,
        texture(gradient, uvw.g).g,
        texture(gradient, uvw.b).b,
        texture(gradient, uvw.a).a
    );
}

#endif // COMMON_COLOR_GLSL
