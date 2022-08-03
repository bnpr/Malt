#ifndef SAMPLER_GLSL
#define SAMPLER_GLSL

/*META 
    @meta: category=Color; subcategory=Color Ramp;
    @u: subtype=Slider; min=0.0; max=1.0;
*/
vec4 sampler1D_sample(sampler1D t, float u) { return texture(t, u); }
/*META @meta: category=Color; subcategory=Color Ramp; */
int sampler1D_size(sampler1D t) { return textureSize(t, 0); }
/*META @meta: category=Color; subcategory=Color Ramp; */
vec4 sampler1D_textel_fetch(sampler1D t, int u) { return texelFetch(t, u, 0); }

/* META
    @meta: subcategory=Image Texture; internal=true;
    @uv: default=UV[0];
*/
vec4 sampler2D_sample(sampler2D t, vec2 uv) { return texture(t, uv); }
/* META 
    @meta: subcategory=Image Texture; internal=true;
    @uv: default=UV[0];
*/
vec4 sampler2D_sample_nearest(sampler2D t, vec2 uv){ return texelFetch(t, ivec2(textureSize(t, 0) * uv), 0); }
/*META @meta: subcategory=Image Texture; internal=true */
ivec2 sampler2D_size(sampler2D t) { return textureSize(t, 0); }
/*META @meta: subcategory=Image Texture; internal=true */
vec4 sampler2D_textel_fetch(sampler2D t, ivec2 uv) { return texelFetch(t, uv, 0); }

#endif //SAMPLER_GLSL
