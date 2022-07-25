#ifndef NODE_UTILS_TEXTURING_GLSL
#define NODE_UTILS_TEXTURING_GLSL

#include "Procedural/Fractal_Noise.glsl"
#include "Procedural/Cell_Noise.glsl"

/*  META GLOBAL
    @meta: category=Texturing;
*/

/*  META
    @UV: default=UV[0];
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
        Color = texelFetch(Image, ivec2(UV*Resolution), 0);
    }
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
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @detail: default=3.0; min=1.0;
    @roughness: subtype=Slider; min=0.0; max=1.0; default = 0.5;
    @tile_size: subtype=Vector; default=vec4(1);
*/
vec4 noise( vec4 coord, float detail, float roughness, bool tile, vec4 tile_size )
{
    return fractal_noise_ex(coord, detail, roughness, tile, tile_size);
}

/* META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @tile_size: subtype=Vector; default = vec4(1.0);
*/
void voronoi( 
    vec4 coord, 
    bool tile, 
    vec4 tile_size,
    out vec4 cell_color,
    out vec3 cell_position,
    out float cell_distance
)
{
    CellNoiseResult result = cell_noise_ex(coord, tile, tile_size);
    cell_color = result.cell_color;
    cell_position = result.cell_position;
    cell_distance = result.cell_distance;
}

#endif //NODE_UTILS_TEXTURING_GLSL