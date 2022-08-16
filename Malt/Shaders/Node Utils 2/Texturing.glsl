#ifndef NODE_UTILS_2_TEXTURING_GLSL
#define NODE_UTILS_2_TEXTURING_GLSL

#include "Procedural/Fractal_Noise.glsl"
#include "Procedural/Cell_Noise.glsl"

/*  META GLOBAL
    @meta: category=Texturing;
*/

/*  META
    @UV: label=UV; default=UV[0];
    @Smooth_Interpolation: default=true;
*/
void Image(sampler2D Image, vec2 UV, bool Smooth_Interpolation, out vec4 Color, out vec2 Resolution)
{
    Resolution = vec2(textureSize(Image, 0));
    if(Smooth_Interpolation)
    {
        Color = texture(Image, UV);
    }
    else
    {
        ivec2 texel = ivec2(mod(UV * Resolution, Resolution));
        Color = texelFetch(Image, texel, 0);
    }
}
/* META
    @UV: label=UV; default=UV[0];
    @UV_Index: label=UV Index;
*/
void Normal_Map(sampler2D Texture, vec2 UV, int UV_Index, out vec3 Normal)
{   
    Normal = sample_normal_map(Texture, UV_Index, UV);
}

/* META
    @tex: label=Texture;
    @uv: label=UV; default=UV[0];
    @page: min=0.0;
*/
vec4 Flipbook(sampler2D tex, vec2 uv, ivec2 dimensions, float page)
{   
    int f = int(floor(page));
    float frac = fract(page);
    vec4 c = sample_flipbook(tex, uv, dimensions, f);
    if(frac == 0.0)
    {
        return c;
    }
    return mix(
        c,
        sample_flipbook(tex, uv, dimensions, f + 1),
        fract(page)
    );
}

/* META
    @tex: label=Texture;
    @uv: label=UV; default=UV[0];
    @flow: default="vec2(0.0)";
    @samples: default=2; min=1 ;
*/
vec4 Flowmap(sampler2D tex, vec2 uv, vec2 flow, float progression, int samples)
{
    return flowmap(tex, uv, flow, progression, samples);
}

/*  META
    @Normal: subtype=Normal; default=NORMAL;
*/
void Matcap(sampler2D Matcap, vec3 Normal, out vec4 Color, out vec2 UV)
{
    UV = matcap_uv(Normal);
    Color = sample_matcap(Matcap, Normal);
}

/*  META
    @meta: label=HDRI;
    @Normal: subtype=Normal; default=NORMAL;
*/
void Hdri(sampler2D Hdri, vec3 Normal, out vec4 Color, out vec2 UV)
{
    UV = hdri_uv(Normal);
    Color = sample_hdri(Hdri, Normal);
}

/*  META
    @meta: subcategory=Noise; label=Infinite;
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @scale: default=5.0;
    @detail: default=3.0; min=1.0;
    @balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
*/
vec4 Noise(vec4 coord, float scale, float detail, float balance)
{
    return fractal_noise_ex(coord * scale, detail, balance, false, vec4(0.0));
}

/*  META
    @meta: subcategory=Noise; label=Tiled;
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @scale: default=5.0;
    @detail: default=3.0; min=1.0;
    @balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
    @tile_size: subtype=Vector; default=vec4(5.0);
*/
vec4 Noise_Tiled(vec4 coord, float scale, float detail, float balance, vec4 tile_size)
{
    return fractal_noise_ex(coord * scale, detail, balance, true, tile_size);
}

/* META
    @meta: subcategory=Voronoi; label=Infinite;
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @scale: default=5.0;
*/
void Voronoi( 
    vec4 coord,
    float scale,
    out vec4 cell_color,
    out vec3 cell_position,
    out float cell_distance
)
{
    CellNoiseResult result = cell_noise_ex(coord * scale, false, vec4(0.0));
    cell_color = result.cell_color;
    cell_position = result.cell_position;
    cell_distance = result.cell_distance;
}

/* META
    @meta: subcategory=Voronoi; label=Tiled;
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @scale: default=5.0;
    @tile_size: subtype=Vector; default = vec4(5.0);
*/
void Voronoi_Tiled(
    vec4 coord,
    float scale,
    vec4 tile_size,
    out vec4 cell_color,
    out vec3 cell_position,
    out float cell_distance
)
{
    CellNoiseResult result = cell_noise_ex(coord * scale, true, tile_size);
    cell_color = result.cell_color;
    cell_position = result.cell_position;
    cell_distance = result.cell_distance;
}

#include "Procedural/Bayer.glsl"

/* META
    @size: subtype=ENUM(2x2,3x3,4x4,8x8); default=2;
    @texel: default=vec2(screen_pixel());
*/
float bayer_pattern(int size, vec2 texel)
{
    switch(size)
    {
        case 0: return bayer_2x2(ivec2(texel));
        case 1: return bayer_3x3(ivec2(texel));
        case 2: return bayer_4x4(ivec2(texel));
        case 3: return bayer_8x8(ivec2(texel));
    }

    return 0;
}
/* META @meta: subcategory=Gradient; label=Linear;*/
float Linear_Gradient(float a)
{
    return clamp(a, 0.0, 1.0);
}
/* META @meta: subcategory=Gradient; label=Quadratic; */
float Quadratic_Gradient(float a)
{
    return clamp(a*a, 0.0, 1.0);
}
/* META @meta: subcategory=Gradient; label=Easing; */
float Easing_Gradient(float a)
{
    float r = clamp(a, 0.0, 1.0);
    float t = r*r;
    return (3.0 * t - 2.0 * t * r);
}
/* META @meta: subcategory=Gradient; label=Diagonal; @a: label=UV;*/
float Diagonal_Gradient(vec2 a)
{
    return (a.x + a.y) * 0.5;
}
/* META @meta: subcategory=Gradient; label=Spherical; @a: label=Vector; subtype=Vector; */
float Spherical_Gradient(vec3 a)
{
    return max(0.999999 - length(a), 0.0);
}
/* META @meta: subcategory=Gradient; label=Quadratic Sphere; @a: label=Vector; subtype=Vector; */
float Quadratic_Sphere_Gradient(vec3 a)
{
    return pow(Spherical_Gradient(a), 2.0);
}
/* META @meta: subcategory=Gradient; label=Radial; @a: label=UV;*/
float Radial_Gradient(vec2 a)
{
    return atan(a.x, a.y) / (M_PI * 2) + 0.5;
}

/* META @meta: label=Wave; @mode: subtype=ENUM(Sine,Saw,Triangle); @a: label=Value; @scale: default=5.0;*/
float Wave_Texture(int mode, float a, float scale, float phase)
{
    switch(mode)
    {
        case 0:
            a = a * scale * M_PI * 2.0 + phase;
            return sin(a - PI/2.0) * 0.5 + 0.5;
        case 1:
            a = a * scale + phase;
            return fract(a);
        case 2:
            a = a * scale + phase;
            return 1.0 - (abs(fract(a) - 0.5) * 2.0);
    }
}

#endif //NODE_UTILS_2_TEXTURING_GLSL
