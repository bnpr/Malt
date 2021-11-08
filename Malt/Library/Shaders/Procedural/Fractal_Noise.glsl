//Copyright (c) 2021 BlenderNPR and contributors. MIT license.

#ifndef PROCEDURAL_FRACTAL_NOISE_GLSL
#define PROCEDURAL_FRACTAL_NOISE_GLSL

#include "Noise.glsl"

vec4 fractal_noise(vec4 coord, int octaves, vec4 tile_size)
{
    vec4 result = vec4(0);
    float strength = 0.5;

    for (int i = 0; i < octaves; i++) 
    {
        result += strength * noise(coord, tile_size);
        coord *= 2.0;
        tile_size *= 2.0;
        strength *= 0.5;
    }
    return result;
}

vec4 fractal_noise(vec4 coord, int octaves)
{
    return fractal_noise(coord, octaves, vec4(0));
}

#endif // PROCEDURAL_FRACTAL_NOISE_GLSL
