#ifndef NODE_UTILS_TEXTURING_GLSL
#define NODE_UTILS_TEXTURING_GLSL

#include "Procedural/Fractal_Noise.glsl"
#include "Procedural/Cell_Noise.glsl"

/* META GLOBAL
    @meta: category=Texturing;
*/

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @detail: default=3.0; min=1.0;
    @roughness: subtype=Slider; min=0.0; max=1.0; default = 0.5;
    @tile_size: subtype=Vector; default=vec4(1);
*/
vec4 noise( vec4 coord, float detail, float roughness, bool tile, vec4 tile_size ){

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
    ) {
        CellNoiseResult result = cell_noise_ex(coord, tile, tile_size);
        cell_color = result.cell_color;
        cell_position = result.cell_position;
        cell_distance = result.cell_distance;
    }

#endif //NODE_UTILS_TEXTURING_GLSL