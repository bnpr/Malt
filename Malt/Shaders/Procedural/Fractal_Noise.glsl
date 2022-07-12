#ifndef PROCEDURAL_FRACTAL_NOISE_GLSL
#define PROCEDURAL_FRACTAL_NOISE_GLSL

#include "Noise.glsl"

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @octaves: default=3;
    @tile_size: subtype=Vector; default=vec4(1);
*/
vec4 fractal_noise_ex(vec4 coord, int octaves, bool tile, vec4 tile_size)
{
    vec4 result = vec4(0);
    float strength = 1.0;
    float total_strength = 0.0;

    for (int i = 0; i < octaves; i++) 
    {   
        vec4 noise = noise_ex(coord, tile, tile_size);
        result += strength * noise;
        total_strength += strength;
        strength *= 0.5;
        coord *= 2.0;
        tile_size *= 2.0;
    }
    return result / total_strength;
}


/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @octaves: default=3;
*/
vec4 fractal_noise(vec4 coord, int octaves)
{
    return fractal_noise_ex(coord, octaves, false, vec4(0));
}

#endif // PROCEDURAL_FRACTAL_NOISE_GLSL
