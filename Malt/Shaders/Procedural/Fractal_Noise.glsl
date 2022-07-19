#ifndef PROCEDURAL_FRACTAL_NOISE_GLSL
#define PROCEDURAL_FRACTAL_NOISE_GLSL

#include "Noise.glsl"

/*  META GLOBAL
    @meta: category=Texturing;
*/

/*  META
    @meta: internal=true;
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @detail: default=3.0; min=1.0;
    @roughness: subtype=Slider; min=0.0; max=1.0; default = 0.5;
    @tile_size: subtype=Vector; default=vec4(1);
*/
vec4 fractal_noise_ex(vec4 coord, float detail, float roughness, bool tile, vec4 tile_size)
{
    vec4 result = vec4(0);
    float weight = 1.0;
    float total_weight = 0.0;
    roughness = clamp(roughness, 0.00001, 1.0);
    detail = max(1.0, detail);

    for (int i = 0; i < ceil(detail); i++) 
    {   
        vec4 noise = noise_ex(coord, tile, tile_size);
        float octave_weight = (i + 1 > floor(detail))? mod(detail, 1.0) : 1.0;
        weight *= roughness * 2 * octave_weight;
        result += weight * noise;
        total_weight += weight;
        coord *= 2.0;
        tile_size *= 2.0;
    }
    return result / total_weight;
}


/*  META
    @meta: internal=true;
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @detail: default=3;
*/
vec4 fractal_noise(vec4 coord, float detail, float roughness)
{
    return fractal_noise_ex(coord, detail, roughness, false, vec4(0));
}

#endif // PROCEDURAL_FRACTAL_NOISE_GLSL
