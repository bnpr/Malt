#ifndef NODE_UTILS_FILTER_GLSL
#define NODE_UTILS_FILTER_GLSL

#include "Filters/Bayer.glsl"

/* META GLOBAL
    @meta: category=Filter;
*/

/* META
    @size: subtype=ENUM(2x2,3x3,4x4,8x8); default=2;
    @uv: label=UV; default=screen_uv() * render_resolution();
*/
float bayer_dithering(int size, vec2 uv)
{
    int num;
    switch(size)
    {
        case 0: num=2; break;
        case 1: num=3; break;
        case 2: num=4; break;
        case 3: num=8; break;
    }
    uv = fract(uv/float(num));
    switch(size)
    {
        case 0: return bayer_mat2(bayer_index(uv, 2));
        case 1: return bayer_mat3(bayer_index(uv, 3));
        case 2: return bayer_mat4(bayer_index(uv, 4));
        case 3: return bayer_mat8(bayer_index(uv, 8));
    }
}

#endif //NODE_UTILS_FILTER_GLSL