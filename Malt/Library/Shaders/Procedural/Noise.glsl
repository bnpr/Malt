//Copyright (c) 2021 BlenderNPR and contributors. MIT license.

#ifndef PROCEDURAL_NOISE_GLSL
#define PROCEDURAL_NOISE_GLSL

#include "Common/Hash.glsl"

vec4 noise(vec4 coord, vec4 tile_size)
{
    tile_size = round(tile_size);
    if(tile_size != vec4(0))
    {
        coord = mod(coord, tile_size);
    }

    vec4 origin = floor(coord);
    vec4 delta = fract(coord);

    //quintic interpolation factor
    vec4 factor = delta*delta*delta*(delta*(delta*6.0-15.0)+10.0);

    vec4 w_results[2];
    for(int w = 0; w <= 1; w++)
    {
        vec4 z_results[2];
        for(int z = 0; z <= 1; z++)
        {
            vec4 y_results[2];
            for(int y = 0; y <= 1; y++)
            {
                vec4 x_results[2];
                for(int x = 0; x <= 1; x++)
                {
                    vec4 offset = vec4(x,y,z,w);
                    vec4 corner = origin + offset;
                    if(tile_size != vec4(0))
                    {
                        corner = mod(corner, tile_size);
                    }
                    vec4 corner_hash_r = hash(corner) * 2.0 - 1.0; //(-1|+1) range
                    vec4 corner_hash_g = hash(corner_hash_r) * 2.0 - 1.0;
                    vec4 corner_hash_b = hash(corner_hash_g) * 2.0 - 1.0;
                    vec4 corner_hash_a = hash(corner_hash_b) * 2.0 - 1.0;
                    x_results[x].r = dot(corner_hash_r, delta-offset);
                    x_results[x].g = dot(corner_hash_g, delta-offset);
                    x_results[x].b = dot(corner_hash_b, delta-offset);
                    x_results[x].a = dot(corner_hash_a, delta-offset);
                }
                y_results[y] = mix(x_results[0], x_results[1], factor.x);
            }
            z_results[z] = mix(y_results[0], y_results[1], factor.y);
        }	
        w_results[w] = mix(z_results[0], z_results[1], factor.z);
    }

    return mix(w_results[0], w_results[1], factor.w) * 0.5 + 0.5;
}

vec4 noise(vec4 coord)
{
    return noise(coord, vec4(0));
}

#endif // PROCEDURAL_NOISE_GLSL
