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
    @coord: subtype=Vector; default=vec4(POSITION,0);
*/
CellNoiseResult cell_noise(vec4 coord)
{
    return cell_noise_ex(coord, false, vec4(0));
}

#endif // PROCEDURAL_CELL_NOISE_GLSL
