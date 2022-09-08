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
    //Kept for backward compatibility
    #define DIMENSIONS 4
    #define T vec4
    if(tile)
    {
        #define TILE 1
        #include "Noise.inl"
        return color;
    }
    else
    {
        #define TILE 0
        #include "Noise.inl"
        return color;
    }
}

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @tile_size: subtype=Vector; default=ivec4(5);
*/
vec4 noise(vec4 coord, ivec4 tile_size)
{
    #define DIMENSIONS 4
    #define T vec4
    #define TILE 1
    #include "Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
*/
vec4 noise(vec4 coord)
{
    #define DIMENSIONS 4
    #define T vec4
    #define TILE 0
    #include "Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION;
    @tile_size: subtype=Vector; default=ivec3(5);
*/
vec4 noise(vec3 coord, ivec3 tile_size)
{
    #define DIMENSIONS 3
    #define T vec3
    #define TILE 1
    #include "Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION;
*/
vec4 noise(vec3 coord)
{
    #define DIMENSIONS 3
    #define T vec3
    #define TILE 0
    #include "Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION.xy;
    @tile_size: subtype=Vector; default=ivec2(5);
*/
vec4 noise(vec2 coord, ivec2 tile_size)
{
    #define DIMENSIONS 2
    #define T vec2
    #define TILE 1
    #include "Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION.xy;
*/
vec4 noise(vec2 coord)
{
    #define DIMENSIONS 2
    #define T vec2
    #define TILE 0
    #include "Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION.x;
    @tile_size: subtype=Vector; default=5;
*/
vec4 noise(float coord, int tile_size)
{
    #define DIMENSIONS 1
    #define T float
    #define TILE 1
    #include "Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION.x;
*/
vec4 noise(float coord)
{
    #define DIMENSIONS 1
    #define T float
    #define TILE 0
    #include "Noise.inl"
    return color;
}

#undef DIMENSIONS
#undef T
#undef TILE

#endif // PROCEDURAL_NOISE_GLSL
