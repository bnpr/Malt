#ifndef NODE_UTILS_2_COLOR_GLSL
#define NODE_UTILS_2_COLOR_GLSL

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

/* META @meta: subcategory=MixRGB; label=Add; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Add(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_add(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Subtract; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Subtract(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_subtract(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Multipy; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Multiply(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_multiply(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Divide; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Divide(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_divide(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Screen; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Screen(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_screen(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Difference; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Difference(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_difference(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Darken; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Darken(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_darken(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Lighten; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Lighten(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_lighten(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Overlay; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Overlay(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_overlay(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Dodge; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Dodge(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_dodge(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Burn; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Burn(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_burn(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Hue; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Hue(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_hue(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Saturation; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Saturation(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_saturation(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Value; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Value(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_value(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Color; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Color(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_color(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Soft Light; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Soft_Light(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_soft_light(Color1, Color2), Blend); }
/* META @meta: subcategory=MixRGB; label=Linear Light; @Blend: subtype=Slider; min=0.0; max=1.0; */
vec4 Mix_Linear_Light(vec4 Color1, vec4 Color2, float Blend){ return mix(Color1, mix_linear_light(Color1, Color2), Blend); }

#endif // NODE_UTILS_2_COLOR_GLSL
