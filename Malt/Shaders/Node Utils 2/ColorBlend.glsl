#ifndef COMMON_BLEND_MODES_GLSL
#define COMMON_BLEND_MODES_GLSL

#include "Common/Color.glsl"

/*  META GLOBAL
    @meta: category=Color; subcategory=Layer Blend;
*/

//Based on https://www.w3.org/TR/compositing-1

void _blend_prepare_inputs(inout vec4 base, inout vec4 blend, int mode, float opacity)
{
    blend.a *= opacity;

    if(mode == 1 || mode == 3)//Clamp
    {
        base = saturate(base);
        blend = saturate(blend);
    }
    if(mode == 2 || mode == 3)//sRGB
    {
        base.rgb = linear_to_srgb(base.rgb);
        blend.rgb = linear_to_srgb(blend.rgb);
    }
}

//https://www.w3.org/TR/compositing-1/#generalformula
vec4 _blend_common(vec4 base, vec4 blend, vec3 mixed, int mode)
{
    if(mode == 1 || mode == 3)//Clamp
    {
        mixed = saturate(mixed);
    }
    vec4 result;
    vec3 color = (1.0 - base.a) * blend.rgb + base.a * mixed;
    result.rgb = color * blend.a + base.rgb * base.a * (1.0 - blend.a);
    result.a = blend.a + base.a * (1.0 - blend.a);
    if(mode == 2 || mode == 3)//sRGB
    {
        result.rgb = srgb_to_linear(result.rgb);
    }
    return result;
}

/*  META
    @meta: label=Normal;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_normal(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    return _blend_common(base, blend, blend.rgb, mode);
}

/*  META
    @meta: label=Add;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_add(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = (base + blend).rgb;
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Multiply;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_multiply(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = (base * blend).rgb;
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Overlay;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_overlay(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed;
    for(int i=0; i<3; i++)
    {
        if(base[i] <= 0.5)
            mixed[i] = blend[i] * 2.0 * base[i];
        else
            mixed[i] = blend[i] + (2.0*base[i]-1.0) - (blend[i] * (2.0*base[i]-1.0));
    }
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Screen;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_screen(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = (base + blend - (base * blend)).rgb;
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Darken;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_darken(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = min(base, blend).rgb;
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Lighten;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_lighten(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = max(base, blend).rgb;
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Soft Light;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_soft_light(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed;
    for(int i=0; i<3; i++)
    {
        float d;
        if(base[i] <= 0.25)
            d = ((16.0*base[i] - 12.0) * base[i] + 4.0) * base[i];
        else
            d = sqrt(base[i]);

        if(blend[i] <= 0.5)
            mixed[i] = base[i] - (1.0 - 2.0*blend[i]) * base[i] * (1.0 - base[i]);
        else
            mixed[i] = base[i] + (2.0*blend[i] - 1.0) * (d - base[i]);
    }
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Hard Light;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_hard_light(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed;
    for(int i=0; i<3; i++)
    {
        if(blend[i] <= 0.5)
            mixed[i] = base[i] * 2.0*blend[i];
        else
            mixed[i] = base[i] + (2.0*blend[i]-1.0) - (base[i] * (2.0*blend[i]-1.0));
    }
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Linear Light;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_linear_light(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = (base + (2.0 * blend) - 1.0).rgb;
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Dodge;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_dodge(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed;
    for(int i=0; i<3; i++)
    {
        if(base[i] == 0)
            mixed[i] = 0;
        else if(blend[i] == 1)
            mixed[i] = 1;
        else
            mixed[i] = min(1.0, base[i] / (1.0 - blend[i]));
    }
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Burn;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_burn(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed;
    for(int i=0; i<3; i++)
    {
        if(base[i] == 1)
            mixed[i] = 1;
        else if(blend[i] == 0)
            mixed[i] = 0;
        else
            mixed[i] = 1 - min(1, (1.0 - base[i]) / blend[i]);
    }
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Subtract;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_subtract(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = (base - blend).rgb;
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Difference;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_difference(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = abs(base - blend).rgb;
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Divide;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_divide(float opacity, vec4 base, vec4 blend, int mode)
{
    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = (base / blend).rgb;
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Hue;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_hue(float opacity, vec4 base, vec4 blend, int mode)
{
    vec3 base_hsv = rgb_to_hsv(base.rgb);
    vec3 blend_hsv = rgb_to_hsv(blend.rgb);
    vec3 mixed_hsv = base_hsv;
    mixed_hsv.x = blend_hsv.x;
    if(blend_hsv.y == 0) mixed_hsv.y = 0;

    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = hsv_to_rgb(mixed_hsv);
    if(mode == 2 || mode == 3)//sRGB
    {
        mixed = linear_to_srgb(mixed);
    }
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Saturation;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_saturation(float opacity, vec4 base, vec4 blend, int mode)
{
    vec3 base_hsv = rgb_to_hsv(base.rgb);
    vec3 blend_hsv = rgb_to_hsv(blend.rgb);
    vec3 mixed_hsv = base_hsv;
    if(base_hsv.y != 0) mixed_hsv.y = blend_hsv.y;

    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = hsv_to_rgb(mixed_hsv);
    if(mode == 2 || mode == 3)//sRGB
    {
        mixed = linear_to_srgb(mixed);
    }
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Value;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_value(float opacity, vec4 base, vec4 blend, int mode)
{
    vec3 base_hsv = rgb_to_hsv(base.rgb);
    vec3 blend_hsv = rgb_to_hsv(blend.rgb);
    vec3 mixed_hsv = base_hsv;
    mixed_hsv.z = blend_hsv.z;

    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = hsv_to_rgb(mixed_hsv);
    if(mode == 2 || mode == 3)//sRGB
    {
        mixed = linear_to_srgb(mixed);
    }
    return _blend_common(base, blend, mixed, mode);
}

/*  META
    @meta: label=Color;
    @blend: default=vec4(0);
    @opacity: subtype=Slider; min=0.0; max=1.0; default=1.0;
    @mode: subtype=ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp);
*/
vec4 blend_color(float opacity, vec4 base, vec4 blend, int mode)
{
    vec3 base_hsv = rgb_to_hsv(base.rgb);
    vec3 blend_hsv = rgb_to_hsv(blend.rgb);
    vec3 mixed_hsv = base_hsv;
    mixed_hsv.xy = blend_hsv.xy;

    _blend_prepare_inputs(base, blend, mode, opacity);
    vec3 mixed = hsv_to_rgb(mixed_hsv);
    if(mode == 2 || mode == 3)//sRGB
    {
        mixed = linear_to_srgb(mixed);
    }
    return _blend_common(base, blend, mixed, mode);
}

#endif //COMMON_BLEND_MODES_GLSL
