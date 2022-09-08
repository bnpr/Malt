#ifndef PROCEDURAL_CELL_NOISE_GLSL
#define PROCEDURAL_CELL_NOISE_GLSL

#include "Common/Hash.glsl"

/*  META GLOBAL
    @meta: category=Texturing; internal=true;
*/

struct CellNoiseResult
{
    vec4 cell_color;
    vec4 cell_position;
    float cell_distance;
};

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @tile_size: subtype=Vector; default=vec4(1);
*/
CellNoiseResult cell_noise_ex(vec4 coord, bool tile, vec4 tile_size)
{
    //Kept for backward compatibility
    CellNoiseResult result;
    #define DIMENSIONS 4
    #define T vec4
    if(tile)
    {
        #define TILE 1
        #include "Cell_Noise.inl"
        result.cell_color = r_cell_color;
        result.cell_position = r_cell_position;
        result.cell_distance = r_cell_distance;
    }
    else
    {
        #define TILE 0
        #include "Cell_Noise.inl"
        result.cell_color = r_cell_color;
        result.cell_position = r_cell_position;
        result.cell_distance = r_cell_distance;
    }
    return result;
}

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
*/
CellNoiseResult cell_noise(vec4 coord)
{
    CellNoiseResult result;
    #define DIMENSIONS 4
    #define T vec4
    #define TILE 0
    #include "Cell_Noise.inl"
    result.cell_color = r_cell_color;
    result.cell_position = r_cell_position;
    result.cell_distance = r_cell_distance;
    return result;
}

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @tile_size: default=ivec4(5);
*/
CellNoiseResult cell_noise(vec4 coord, ivec4 tile_size)
{
    CellNoiseResult result;
    #define DIMENSIONS 4
    #define T vec4
    #define TILE 1
    #include "Cell_Noise.inl"
    result.cell_color = r_cell_color;
    result.cell_position = r_cell_position;
    result.cell_distance = r_cell_distance;
    return result;
}

/*  META
    @coord: subtype=Vector; default=vec3(POSITION);
*/
CellNoiseResult cell_noise(vec3 coord)
{
    CellNoiseResult result;
    #define DIMENSIONS 3
    #define T vec3
    #define TILE 0
    #include "Cell_Noise.inl"
    result.cell_color = r_cell_color;
    result.cell_position.xyz = r_cell_position;
    result.cell_distance = r_cell_distance;
    return result;
}

/*  META
    @coord: subtype=Vector; default=POSITION;
    @tile_size: default=ivec3(5);
*/
CellNoiseResult cell_noise(vec3 coord, ivec3 tile_size)
{
    CellNoiseResult result;
    #define DIMENSIONS 3
    #define T vec3
    #define TILE 1
    #include "Cell_Noise.inl"
    result.cell_color = r_cell_color;
    result.cell_position.xyz = r_cell_position;
    result.cell_distance = r_cell_distance;
    return result;
}

/*  META
    @coord: subtype=Vector; default=POSITION.xy;
*/
CellNoiseResult cell_noise(vec2 coord)
{
    CellNoiseResult result;
    #define DIMENSIONS 2
    #define T vec2
    #define TILE 0
    #include "Cell_Noise.inl"
    result.cell_color = r_cell_color;
    result.cell_position.xy = r_cell_position;
    result.cell_distance = r_cell_distance;
    return result;
}

/*  META
    @coord: subtype=Vector; default=POSITION.xy;
    @tile_size: default=ivec2(5);
*/
CellNoiseResult cell_noise(vec2 coord, ivec2 tile_size)
{
    CellNoiseResult result;
    #define DIMENSIONS 2
    #define T vec2
    #define TILE 1
    #include "Cell_Noise.inl"
    result.cell_color = r_cell_color;
    result.cell_position.xy = r_cell_position;
    result.cell_distance = r_cell_distance;
    return result;
}

/*  META
    @coord: subtype=Vector; default=POSITION.x;
*/
CellNoiseResult cell_noise(float coord)
{
    CellNoiseResult result;
    #define DIMENSIONS 1
    #define T float
    #define TILE 0
    #include "Cell_Noise.inl"
    result.cell_color = r_cell_color;
    result.cell_position.x = r_cell_position;
    result.cell_distance = r_cell_distance;
    return result;
}

/*  META
    @coord: subtype=Vector; default=POSITION.x;
    @tile_size: default=5;
*/
CellNoiseResult cell_noise(float coord, int tile_size)
{
    CellNoiseResult result;
    #define DIMENSIONS 1
    #define T float
    #define TILE 1
    #include "Cell_Noise.inl"
    result.cell_color = r_cell_color;
    result.cell_position.x = r_cell_position;
    result.cell_distance = r_cell_distance;
    return result;
}

#undef DIMENSIONS
#undef T
#undef TILE

#endif // PROCEDURAL_CELL_NOISE_GLSL
