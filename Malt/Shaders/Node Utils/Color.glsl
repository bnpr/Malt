#ifndef NODE_UTILS_COLOR_GLSL
#define NODE_UTILS_COLOR_GLSL

/*  META GLOBAL
    @meta: category=Color;
*/

/*  META 
    @meta: label=Gradient; subcategory=Color Gradient;
    @Coord: label=U; subtype=Slider; min=0.0; max=1.0;
*/
vec4 Color_Gradient_1d(sampler1D Color_Ramp, float Coord) { return texture(Color_Ramp, Coord); }

/*  META 
    @meta: label=RGB Gradient; subcategory=Color Gradient;
    @Coord: label=UVW; subtype=Slider; min=0.0; max=1.0;
*/
vec3 Color_Gradient_3d(sampler1D Color_Ramp, vec3 Coord) { return rgb_gradient(Color_Ramp, Coord); }

/*  META 
    @meta: label=RGBA Gradient; subcategory=Color Gradient;
    @Coord: label=UVWX; subtype=Slider; min=0.0; max=1.0;
*/
vec4 Color_Gradient_4d(sampler1D Color_Ramp, vec4 Coord) { return rgba_gradient(Color_Ramp, Coord); }

#endif // NODE_UTILS_COLOR_GLSL
