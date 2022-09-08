#ifndef PROCEDURAL_NOISE_GLSL
#define PROCEDURAL_NOISE_GLSL

#include "Common/Hash.glsl"

/*  META GLOBAL
    @meta: internal=true;
*/

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @tile_size: subtype=Vector; default=vec4(1);
*/
vec4 noise_ex(vec4 coord, bool tile, vec4 tile_size)
{
    float magic_multiplier = 0.78;
    tile_size = round(tile_size);
    if(tile)
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
                    if(tile)
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

    return mix(w_results[0], w_results[1], factor.w) * magic_multiplier + 0.5;
}

/*  META
    @coord: subtype=Vector; default=POSITION;
    @tile_size: subtype=Vector; default=vec3(1);
*/
vec4 noise_ex(vec3 coord, bool tile, vec3 tile_size)
{
    float magic_multiplier = 0.78;
    tile_size = round(tile_size);
    if(tile)
    {
        coord = mod(coord, tile_size);
    }

    vec3 origin = floor(coord);
    vec3 delta = fract(coord);

    //quintic interpolation factor
    vec3 factor = delta*delta*delta*(delta*(delta*6.0-15.0)+10.0);

    vec4 z_results[2];
    for(int z = 0; z <= 1; z++)
    {
        vec4 y_results[2];
        for(int y = 0; y <= 1; y++)
        {
            vec4 x_results[2];
            for(int x = 0; x <= 1; x++)
            {
                vec3 offset = vec3(x,y,z);
                vec3 corner = origin + offset;
                if(tile)
                {
                    corner = mod(corner, tile_size);
                }
                vec3 corner_hash_r = hash(corner).xyz * 2.0 - 1.0; //(-1|+1) range
                vec3 corner_hash_g = hash(corner_hash_r).xyz * 2.0 - 1.0;
                vec3 corner_hash_b = hash(corner_hash_g).xyz * 2.0 - 1.0;
                vec3 corner_hash_a = hash(corner_hash_b).xyz * 2.0 - 1.0;
                x_results[x].r = dot(corner_hash_r, delta-offset);
                x_results[x].g = dot(corner_hash_g, delta-offset);
                x_results[x].b = dot(corner_hash_b, delta-offset);
                x_results[x].a = dot(corner_hash_a, delta-offset);
            }
            y_results[y] = mix(x_results[0], x_results[1], factor.x);
        }
        z_results[z] = mix(y_results[0], y_results[1], factor.y);
    }	

    return mix(z_results[0], z_results[1], factor.z) * magic_multiplier + 0.5;
}

/*  META
    @coord: default=UV[0];
    @tile_size: default=vec2(1);
*/
vec4 noise_ex(vec2 coord, bool tile, vec2 tile_size)
{
    float magic_multiplier = 0.9;
    tile_size = round(tile_size);
    if(tile)
    {
        coord = mod(coord, tile_size);
    }

    vec2 origin = floor(coord);
    vec2 delta = fract(coord);

    //quintic interpolation factor
    vec2 factor = delta*delta*delta*(delta*(delta*6.0-15.0)+10.0);


    vec4 y_results[2];
    for(int y = 0; y <= 1; y++)
    {
        vec4 x_results[2];
        for(int x = 0; x <= 1; x++)
        {
            vec2 offset = vec2(x,y);
            vec2 corner = origin + offset;
            if(tile)
            {
                corner = mod(corner, tile_size);
            }
            vec2 corner_hash_r = hash(corner).xy * 2.0 - 1.0; //(-1|+1) range
            vec2 corner_hash_g = hash(corner_hash_r).xy * 2.0 - 1.0;
            vec2 corner_hash_b = hash(corner_hash_g).xy * 2.0 - 1.0;
            vec2 corner_hash_a = hash(corner_hash_b).xy * 2.0 - 1.0;
            x_results[x].r = dot(corner_hash_r, delta-offset);
            x_results[x].g = dot(corner_hash_g, delta-offset);
            x_results[x].b = dot(corner_hash_b, delta-offset);
            x_results[x].a = dot(corner_hash_a, delta-offset);
        }
        y_results[y] = mix(x_results[0], x_results[1], factor.x);
    }

    return mix(y_results[0], y_results[1], factor.y) * magic_multiplier + 0.5;
}

/*  META
    @coord: default=UV[0].x;
    @tile_size: default=1.0;
*/
vec4 noise_ex(float coord, bool tile, float tile_size)
{
    float magic_multiplier = 1.08;
    tile_size = round(tile_size);
    if(tile)
    {
        coord = mod(coord, tile_size);
    }

    float origin = floor(coord);
    float delta = fract(coord);

    //quintic interpolation factor
    float factor = delta*delta*delta*(delta*(delta*6.0-15.0)+10.0);


    vec4 x_results[2];
    for(int x = 0; x <= 1; x++)
    {
        float offset = float(x);
        float corner = origin + offset;
        if(tile)
        {
            corner = mod(corner, tile_size);
        }
        vec4 corner_hash = hash(corner) * 2.0 - 1.0; //(-1|+1) range
        x_results[x].r = dot(corner_hash.x, delta-offset);
        x_results[x].g = dot(corner_hash.y, delta-offset);
        x_results[x].b = dot(corner_hash.z, delta-offset);
        x_results[x].a = dot(corner_hash.w, delta-offset);
    }

    return mix(x_results[0], x_results[1], factor) * magic_multiplier + 0.5;
}

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
*/
vec4 noise(vec4 coord)
{
    return noise_ex(coord, false, vec4(0));
}

/*  META
    @coord: subtype=Vector; default=POSITION;
*/
vec4 noise(vec3 coord)
{
    return noise_ex(coord, false, vec3(0));
}

/*  META
    @coord: default=UV[0];
*/
vec4 noise(vec2 coord)
{
    return noise_ex(coord, false, vec2(0));
}

/*  META
    @coord: default=UV[0].x;
*/
vec4 noise(float coord)
{
    return noise_ex(coord, false, 0.0);
}

#endif // PROCEDURAL_NOISE_GLSL
