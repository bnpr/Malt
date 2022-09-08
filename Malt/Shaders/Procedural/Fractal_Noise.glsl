#ifndef PROCEDURAL_FRACTAL_NOISE_GLSL
#define PROCEDURAL_FRACTAL_NOISE_GLSL

#include "Noise.glsl"

/*  META GLOBAL
    @meta: category=Texturing; @meta: internal=true;
*/

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @detail: default=3.0; min=1.0;
    @detail_balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
    @tile_size: subtype=Vector; default=vec4(1);
*/
vec4 fractal_noise_ex(vec4 coord, float detail, float detail_balance, bool tile, vec4 tile_size)
{
    vec4 result = vec4(0);
    float weight = 1.0;
    float total_weight = 0.0;
    detail_balance = clamp(detail_balance, 0.00001, 1.0);
    detail = max(1.0, detail);

    for (int i = 0; i < ceil(detail); i++) 
    {   
        vec4 noise = noise_ex(coord, tile, tile_size);
        float octave_weight = (i + 1 > floor(detail))? mod(detail, 1.0) : 1.0;
        weight *= detail_balance * 2 * octave_weight;
        result += weight * noise;
        total_weight += weight;
        coord *= 2.0;
        tile_size *= 2.0;
    }
    return result / total_weight;
}

/*  META
    @coord: subtype=Vector; default=POSITION;
    @detail: default=3.0; min=1.0;
    @detail_balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
    @tile_size: subtype=Vector; default=vec3(1);
*/
vec4 fractal_noise_ex(vec3 coord, float detail, float detail_balance, bool tile, vec3 tile_size)
{
    vec4 result = vec4(0);
    float weight = 1.0;
    float total_weight = 0.0;
    detail_balance = clamp(detail_balance, 0.00001, 1.0);
    detail = max(1.0, detail);

    for (int i = 0; i < ceil(detail); i++) 
    {   
        vec4 noise = noise_ex(coord, tile, tile_size);
        float octave_weight = (i + 1 > floor(detail))? mod(detail, 1.0) : 1.0;
        weight *= detail_balance * 2 * octave_weight;
        result += weight * noise;
        total_weight += weight;
        coord *= 2.0;
        tile_size *= 2.0;
    }
    return result / total_weight;
}

/*  META
    @coord: default=UV[0];
    @detail: default=3.0; min=1.0;
    @detail_balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
    @tile_size: default=vec2(1);
*/
vec4 fractal_noise_ex(vec2 coord, float detail, float detail_balance, bool tile, vec2 tile_size)
{
    vec4 result = vec4(0);
    float weight = 1.0;
    float total_weight = 0.0;
    detail_balance = clamp(detail_balance, 0.00001, 1.0);
    detail = max(1.0, detail);

    for (int i = 0; i < ceil(detail); i++) 
    {   
        vec4 noise = noise_ex(coord, tile, tile_size);
        float octave_weight = (i + 1 > floor(detail))? mod(detail, 1.0) : 1.0;
        weight *= detail_balance * 2 * octave_weight;
        result += weight * noise;
        total_weight += weight;
        coord *= 2.0;
        tile_size *= 2.0;
    }
    return result / total_weight;
}

/*  META
    @coord: default=UV[0].x;
    @detail: default=3.0; min=1.0;
    @detail_balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
    @tile_size: default=1.0;
*/
vec4 fractal_noise_ex(float coord, float detail, float detail_balance, bool tile, float tile_size)
{
    vec4 result = vec4(0);
    float weight = 1.0;
    float total_weight = 0.0;
    detail_balance = clamp(detail_balance, 0.00001, 1.0);
    detail = max(1.0, detail);

    for (int i = 0; i < ceil(detail); i++) 
    {   
        vec4 noise = noise_ex(coord, tile, tile_size);
        float octave_weight = (i + 1 > floor(detail))? mod(detail, 1.0) : 1.0;
        weight *= detail_balance * 2 * octave_weight;
        result += weight * noise;
        total_weight += weight;
        coord *= 2.0;
        tile_size *= 2.0;
    }
    return result / total_weight;
}

// Keep for backwards compatibility
vec4 fractal_noise_ex(vec4 coord, int octaves, bool tile, vec4 tile_size){
    return fractal_noise_ex(coord, float(octaves), 0.5, tile, tile_size);
}


/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @detail: default=3;
*/
vec4 fractal_noise(vec4 coord, int octaves)
{
    return fractal_noise_ex(coord, float(octaves), 0.0, false, vec4(0));
}

/*  META
    @coord: subtype=Vector; default=POSITION;
    @detail: default=3;
*/
vec4 fractal_noise(vec3 coord, int octaves)
{
    return fractal_noise_ex(coord, float(octaves), 0.0, false, vec3(0));
}

/*  META
    @coord: default=UV[0];
    @detail: default=3;
*/
vec4 fractal_noise(vec2 coord, int octaves)
{
    return fractal_noise_ex(coord, float(octaves), 0.0, false, vec2(0));
}

/*  META
    @coord: default=UV[0].x;
    @detail: default=3;
*/
vec4 fractal_noise(float coord, int octaves)
{
    return fractal_noise_ex(coord, float(octaves), 0.0, false, 0.0);
}

#endif // PROCEDURAL_FRACTAL_NOISE_GLSL
