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

/* META @meta: label=Grayscale; */
float relative_luminance(vec3 color)
{
    return dot(color, vec3(0.2126,0.7152,0.0722));
}

/* META @meta: internal=true; */
float luma(vec3 color)
{
    return dot(color, vec3(0.299,0.587,0.114));
}

/* META @meta: label=Linear To sRGB; */
vec3 linear_to_srgb(vec3 linear)
{
    vec3 low = linear * 12.92;
    vec3 high = 1.055 * pow(linear, vec3(1.0/2.4)) - 0.055;
    return mix(low, high, greaterThan(linear, vec3(0.0031308)));
}

/* META @meta: label=sRGB To Linear; */
vec3 srgb_to_linear(vec3 srgb)
{
    vec3 low = srgb / 12.92;
    vec3 high = pow((srgb + 0.055)/1.055, vec3(2.4));
    return mix(low, high, greaterThan(srgb, vec3(0.04045)));
}

/* META @meta: label=RGB To HSV; */
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
    @meta: label=HSV To RGB;
    @hsv:subtype=HSV;
*/
vec3 hsv_to_rgb(vec3 hsv)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(hsv.xxx + K.xyz) * 6.0 - K.www);
    return srgb_to_linear(hsv.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), hsv.y));
}

/* META @meta: label=HSV Edit; */
vec4 hsv_edit(vec4 color, float hue, float saturation, float value)
{
    vec3 hsv = rgb_to_hsv(color.rgb);
    hsv += vec3(hue, saturation, value);
    return vec4(hsv_to_rgb(hsv), color.a);
}

/* META @meta: label=Bright/Contrast; */
vec4 bright_contrast(vec4 color, float brightness, float contrast)
{
    float a = 1.0 + contrast;
    float b = brightness - contrast * 0.5;
    vec3 result = max(a * color.rgb + b, vec3(0.0));
    return vec4(result, color.a);
}
/* META 
    @meta: label=Gamma; 
    @gamma: default=1.0; min=0.0;
*/
vec4 gamma_correction(vec4 color, float gamma)
{
    vec3 result = max(pow(color.rgb, vec3(gamma)), vec3(0));
    return vec4(result, color.a);
}

/* META 
    @meta: label=Invert; 
    @fac: subtype=Slider; min=0.0; max=1.0;
*/
vec4 color_invert(vec4 color, float fac)
{
    vec4 inverted = vec4(1.0 - color.rgb, color.a);
    return mix(color, inverted, fac);
}

/* META @meta: internal=true; */
vec3 rgb_gradient(sampler1D gradient, vec3 uvw)
{
    return vec3
    (
        texture(gradient, uvw.r).r,
        texture(gradient, uvw.g).g,
        texture(gradient, uvw.b).b
    );
}

/* META @meta: internal=true; */
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
