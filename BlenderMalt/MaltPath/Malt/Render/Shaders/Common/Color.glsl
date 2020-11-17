//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef COMMON_COLOR_GLSL
#define COMMON_COLOR_GLSL

float luma(vec3 color)
{
    return dot(color, vec3(0.299,0.587,0.114));
}

//http://lolengine.net/blog/2013/07/27/rgb-to-hsv-in-glsl
vec3 rgb_to_hsv(vec3 rgb)
{
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = rgb.g < rgb.b ? vec4(rgb.bg, K.wz) : vec4(rgb.gb, K.xy);
    vec4 q = rgb.r < p.x ? vec4(p.xyw, rgb.r) : vec4(rgb.r, p.yzx);

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv_to_rgb(vec3 hsv)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(hsv.xxx + K.xyz) * 6.0 - K.www);
    return hsv.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), hsv.y);
}

vec4 alpha_blend(vec4 base, vec4 blend)
{
    float alpha = blend.a + base.a * (1.0 - blend.a);
    vec4 result = (blend * blend.a + base * base.a * (1.0 - blend.a)) / alpha;
    result.a = alpha;

    return result;
}

#endif // COMMON_COLOR_GLSL
