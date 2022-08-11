#ifndef COMMON_MIXRGB_GLSL
#define COMMON_MIXRGB_GLSL

/*  META GLOBAL
    @meta: internal=true;
*/

vec4 mix_add(vec4 col1, vec4 col2){ return col1 + vec4(col2.rgb, 0.0); }

vec4 mix_subtract(vec4 col1, vec4 col2){ return col1 - vec4(col2.rgb, 0.0); }

vec4 mix_multiply(vec4 col1, vec4 col2){ return col1 * vec4(col2.rgb, 1.0); }

vec4 mix_divide(vec4 col1, vec4 col2)
{

    vec4 result = col1;

    if (col2.r > 0.0) {
        result.r = result.r / col2.r;
    }
    if (col2.g > 0.0) {
        result.g = result.g / col2.g;
    }
    if (col2.b > 0.0) {
        result.b = result.b / col2.b;
    }
    return result;
}

vec4 mix_screen(vec4 col1, vec4 col2)
{
    vec4 result = vec4(1.0) - ((vec4(1.0) - col2)) * (vec4(1.0) - col1);
    result.a = col1.a;
    return result;
}

vec4 mix_difference(vec4 col1, vec4 col2)
{
    vec4 result = abs(col1 - col2);
    return result;
}

vec4 mix_darken(vec4 col1, vec4 col2){ return min(col1, col2); }

vec4 mix_lighten(vec4 col1, vec4 col2){ return max(col1, col2); }

vec4 mix_overlay(vec4 col1, vec4 col2)
{
    vec4 result = col1;

    if (result.r < 0.5) {
        result.r *= 2.0 * col2.r;
    }
    else {
        result.r = 1.0 - (2.0 * (1.0 - col2.r)) * (1.0 - result.r);
    }

    if (result.g < 0.5) {
        result.g *= 2.0 * col2.g;
    }
    else {
        result.g = 1.0 - (2.0 * (1.0 - col2.g)) * (1.0 - result.g);
    }

    if (result.b < 0.5) {
        result.b *= 2.0 * col2.b;
    }
    else {
        result.b = 1.0 - (2.0 * (1.0 - col2.b)) * (1.0 - result.b);
    }
    return result;
}

vec4 mix_dodge(vec4 col1, vec4 col2)
{
    vec4 result = col1;

    if (result.r != 0.0) {
        float tmp = 1.0 - col2.r;
        if (tmp <= 0.0) {
        result.r = 1.0;
        }
        else if ((tmp = result.r / tmp) > 1.0) {
        result.r = 1.0;
        }
        else {
        result.r = tmp;
        }
    }
    if (result.g != 0.0) {
        float tmp = 1.0 - col2.g;
        if (tmp <= 0.0) {
        result.g = 1.0;
        }
        else if ((tmp = result.g / tmp) > 1.0) {
        result.g = 1.0;
        }
        else {
        result.g = tmp;
        }
    }
    if (result.b != 0.0) {
        float tmp = 1.0 - col2.b;
        if (tmp <= 0.0) {
        result.b = 1.0;
        }
        else if ((tmp = result.b / tmp) > 1.0) {
        result.b = 1.0;
        }
        else {
        result.b = tmp;
        }
    }
    return result;
}

vec4 mix_burn(vec4 col1, vec4 col2)
{
    vec4 result = col1;

    float tmp = col2.r;
    if (tmp <= 0.0) {
        result.r = 0.0;
    }
    else if ((tmp = (1.0 - (1.0 - result.r) / tmp)) < 0.0) {
        result.r = 0.0;
    }
    else if (tmp > 1.0) {
        result.r = 1.0;
    }
    else {
        result.r = tmp;
    }

    tmp = col2.g;
    if (tmp <= 0.0) {
        result.g = 0.0;
    }
    else if ((tmp = (1.0 - (1.0 - result.g) / tmp)) < 0.0) {
        result.g = 0.0;
    }
    else if (tmp > 1.0) {
        result.g = 1.0;
    }
    else {
        result.g = tmp;
    }

    tmp = col2.b;
    if (tmp <= 0.0) {
        result.b = 0.0;
    }
    else if ((tmp = (1.0 - (1.0 - result.b) / tmp)) < 0.0) {
        result.b = 0.0;
    }
    else if (tmp > 1.0) {
        result.b = 1.0;
    }
    else {
        result.b = tmp;
    }
    return result;
}

vec4 mix_hue(vec4 col1, vec4 col2)
{
    vec4 result = col1;

    vec4 hsv, hsv2;
    hsv2.rgb = rgb_to_hsv(col2.rgb);

    if (hsv2.y != 0.0) {
        hsv.rgb = rgb_to_hsv(result.rgb);
        hsv.x = hsv2.x;
        result.rgb = hsv_to_rgb(hsv.rgb);
    }
    return result;
}

vec4 mix_saturation(vec4 col1, vec4 col2)
{
    vec4 result = col1;

    vec4 hsv, hsv2;
    hsv.rgb = rgb_to_hsv(result.rgb);

    if (hsv.y != 0.0) {
        hsv2.rgb = rgb_to_hsv(col2.rgb);

        hsv.y = hsv2.y;
        result.rgb = hsv_to_rgb(hsv.rgb);
    }
    return result;
}

vec4 mix_value(vec4 col1, vec4 col2)
{
    vec4 hsv, hsv2;
    hsv.rgb = rgb_to_hsv(col1.rgb);
    hsv2.rgb = rgb_to_hsv(col2.rgb);

    hsv.z = hsv2.z;
    vec4 result = col1;
    result.rgb = hsv_to_rgb(hsv.rgb);
    return result;
}

vec4 mix_color(vec4 col1, vec4 col2)
{
    vec4 result = col1;

    vec4 hsv, hsv2;
    hsv2.rgb = rgb_to_hsv(col2.rgb);

    if (hsv2.y != 0.0) {
        hsv.rgb = rgb_to_hsv(result.rgb);
        hsv.x = hsv2.x;
        hsv.y = hsv2.y;
        result.rgb = hsv_to_rgb(hsv.rgb);
    }
    return result;
}

vec4 mix_soft_light(vec4 col1, vec4 col2)
{
    vec4 one = vec4(1.0);
    vec4 scr = one - (one - col2) * (one - col1);
    return ((one - col1) * col2 * col1 + col1 * scr);
}

vec4 mix_linear_light(vec4 col1, vec4 col2)
{
    return col1 + (2.0 * (col2 - vec4(0.5)));
}

#endif //COMMON_MIXRGB_GLSL
