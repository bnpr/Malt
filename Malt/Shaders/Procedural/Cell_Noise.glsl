#ifndef PROCEDURAL_CELL_NOISE_GLSL
#define PROCEDURAL_CELL_NOISE_GLSL

#include "Common/Hash.glsl"

/*  META GLOBAL
    @meta: category=Texturing; internal=true;
*/

struct CellNoiseResult
{
    vec4 cell_color;
    vec3 cell_position;
    float cell_distance;
};

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @tile_size: subtype=Vector; default=vec4(1);
*/
CellNoiseResult cell_noise_ex(vec4 coord, bool tile, vec4 tile_size)
{
    vec4 real_coord = coord;
    tile_size = round(tile_size);
    if(tile)
    {
        coord = mod(coord, tile_size);
    }

    vec4 real_origin = floor(real_coord) + 0.5;
    vec4 origin = floor(coord) + 0.5;
    vec4 delta = fract(coord);

    CellNoiseResult r;
    r.cell_distance = 10;

    for(int z = -1; z <= 1; z++)
    {
        for(int y = -1; y <= 1; y++)
        {
            for(int x = -1; x <= 1; x++)
            {
                vec4 offset = vec4(x,y,z,0);
                vec4 real_corner = real_origin + offset;
                vec4 corner = origin + offset;
                vec4 next_corner = corner + vec4(0,0,0,1);
                if(tile)
                {
                    corner = mod(corner, tile_size);
                    next_corner = mod(next_corner, tile_size);
                }
                vec4 corner_hash = mix(hash(corner), hash(next_corner), delta.w);
                vec4 real_cell_position = real_corner + (corner_hash - 0.5);
                vec4 cell_position = corner + (corner_hash - 0.5);
                float cell_distance = distance(real_coord.xyz, real_cell_position.xyz);
                if(cell_distance < r.cell_distance)
                {
                    r.cell_color = hash(corner.xyz);
                    r.cell_position = real_cell_position.xyz;
                    r.cell_distance = cell_distance;
                }
            }
        }
    }	

    return r;
}

/*  META
    @coord: subtype=Vector; default=POSITION;
    @tile_size: subtype=Vector; default=vec3(1);
*/
CellNoiseResult cell_noise_ex(vec3 coord, bool tile, vec3 tile_size)
{
    vec3 real_coord = coord;
    tile_size = round(tile_size);
    if(tile)
    {
        coord = mod(coord, tile_size);
    }

    vec3 real_origin = floor(real_coord) + 0.5;
    vec3 origin = floor(coord) + 0.5;
    vec3 delta = fract(coord);

    CellNoiseResult r;
    r.cell_distance = 10;

    for(int z = -1; z <= 1; z++)
    {
        for(int y = -1; y <= 1; y++)
        {
            for(int x = -1; x <= 1; x++)
            {
                vec3 offset = vec3(x,y,z);
                vec3 real_corner = real_origin + offset;
                vec3 corner = origin + offset;
                vec3 next_corner = corner;
                if(tile)
                {
                    corner = mod(corner, tile_size);
                    next_corner = mod(next_corner, tile_size);
                }
                vec3 corner_hash = hash(corner).rgb;
                vec3 real_cell_position = real_corner + (corner_hash - 0.5);
                vec3 cell_position = corner + (corner_hash - 0.5);
                float cell_distance = distance(real_coord, real_cell_position);
                if(cell_distance < r.cell_distance)
                {
                    r.cell_color = hash(corner);
                    r.cell_position = real_cell_position;
                    r.cell_distance = cell_distance;
                }
            }
        }
    }	

    return r;
}

/*  META
    @coord: default=UV[0];
    @tile_size: default=vec2(1);
*/
CellNoiseResult cell_noise_ex(vec2 coord, bool tile, vec2 tile_size)
{
    vec2 real_coord = coord;
    tile_size = round(tile_size);
    if(tile)
    {
        coord = mod(coord, tile_size);
    }

    vec2 real_origin = floor(real_coord) + 0.5;
    vec2 origin = floor(coord) + 0.5;
    vec2 delta = fract(coord);

    CellNoiseResult r;
    r.cell_distance = 10;


    for(int y = -1; y <= 1; y++)
    {
        for(int x = -1; x <= 1; x++)
        {
            vec2 offset = vec2(x,y);
            vec2 real_corner = real_origin + offset;
            vec2 corner = origin + offset;
            vec2 next_corner = corner;
            if(tile)
            {
                corner = mod(corner, tile_size);
                next_corner = mod(next_corner, tile_size);
            }
            vec2 corner_hash = hash(corner).xy;
            vec2 real_cell_position = real_corner + (corner_hash - 0.5);
            vec2 cell_position = corner + (corner_hash - 0.5);
            float cell_distance = distance(real_coord, real_cell_position);
            if(cell_distance < r.cell_distance)
            {
                r.cell_color = hash(corner);
                r.cell_position = vec3(real_cell_position, 0.0);
                r.cell_distance = cell_distance;
            }
        }
    }
	

    return r;
}

/*  META
    @coord: default=UV[0].x;
    @tile_size: default=1.0;
*/
CellNoiseResult cell_noise_ex(float coord, bool tile, float tile_size)
{
    float real_coord = coord;
    tile_size = round(tile_size);
    if(tile)
    {
        coord = mod(coord, tile_size);
    }

    float real_origin = floor(real_coord) + 0.5;
    float origin = floor(coord) + 0.5;
    float delta = fract(coord);

    CellNoiseResult r;
    r.cell_distance = 10;


    for(int x = -1; x <= 1; x++)
    {
        float offset = x;
        float real_corner = real_origin + offset;
        float corner = origin + offset;
        float next_corner = corner;
        if(tile)
        {
            corner = mod(corner, tile_size);
            next_corner = mod(next_corner, tile_size);
        }
        float corner_hash = hash(corner).x;
        float real_cell_position = real_corner + (corner_hash - 0.5);
        float cell_position = corner + (corner_hash - 0.5);
        float cell_distance = distance(real_coord, real_cell_position);
        if(cell_distance < r.cell_distance)
        {
            r.cell_color = hash(corner);
            r.cell_position = vec3(real_cell_position, 0.0, 0.0);
            r.cell_distance = cell_distance;
        }
    }
	

    return r;
}

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
*/
CellNoiseResult cell_noise(vec4 coord)
{
    return cell_noise_ex(coord, false, vec4(0));
}

/*  META
    @coord: subtype=Vector; default=POSITION;
*/
CellNoiseResult cell_noise(vec3 coord)
{
    return cell_noise_ex(coord, false, vec3(0));
}

/*  META
    @coord: default=UV[0];
*/
CellNoiseResult cell_noise(vec2 coord)
{
    return cell_noise_ex(coord, false, vec2(0));
}

/*  META
    @coord: default=UV[0].x;
*/
CellNoiseResult cell_noise(float coord)
{
    return cell_noise_ex(coord, false, 0.0);
}

#endif // PROCEDURAL_CELL_NOISE_GLSL
