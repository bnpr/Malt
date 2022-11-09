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
    @tile_size: default=ivec4(5);
*/
vec4 fractal_noise(vec4 coord, float detail, float detail_balance, ivec4 tile_size)
{
    #define TILE 1
    #include "Fractal_Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=vec4(POSITION,0);
    @detail: default=3.0; min=1.0;
    @detail_balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
*/
vec4 fractal_noise(vec4 coord, float detail, float detail_balance)
{
    #define TILE 0
    #include "Fractal_Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION;
    @detail: default=3.0; min=1.0;
    @detail_balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
    @tile_size: default=ivec3(5);
*/
vec4 fractal_noise(vec3 coord, float detail, float detail_balance, ivec3 tile_size)
{
    #define TILE 1
    #include "Fractal_Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION;
    @detail: default=3.0; min=1.0;
    @detail_balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
*/
vec4 fractal_noise(vec3 coord, float detail, float detail_balance)
{
    #define TILE 0
    #include "Fractal_Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION.xy;
    @detail: default=3.0; min=1.0;
    @detail_balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
    @tile_size: default=ivec2(5);
*/
vec4 fractal_noise(vec2 coord, float detail, float detail_balance, ivec2 tile_size)
{
    #define TILE 1
    #include "Fractal_Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION.xy;
    @detail: default=3.0; min=1.0;
    @detail_balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
*/
vec4 fractal_noise(vec2 coord, float detail, float detail_balance)
{
    #define TILE 0
    #include "Fractal_Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION.x;
    @detail: default=3.0; min=1.0;
    @detail_balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
    @tile_size: default=5;
*/
vec4 fractal_noise(float coord, float detail, float detail_balance, int tile_size)
{
    #define TILE 1
    #include "Fractal_Noise.inl"
    return color;
}

/*  META
    @coord: subtype=Vector; default=POSITION.x;
    @detail: default=3.0; min=1.0;
    @detail_balance: subtype=Slider; min=0.0; max=1.0; default = 0.5;
*/
vec4 fractal_noise(float coord, float detail, float detail_balance)
{
    #define TILE 0
    #include "Fractal_Noise.inl"
    return color;
}

#undef TILE

// Keep for backward compatibility
vec4 fractal_noise_ex(vec4 coord, int octaves, bool tile, vec4 tile_size)
{
    if(tile)
    {
        return fractal_noise(coord, float(octaves), 0.5, ivec4(tile_size));
    }
    else
    {
        return fractal_noise(coord, float(octaves), 0.5);
    }
}
vec4 fractal_noise(vec4 coord, int octaves)
{
    return fractal_noise(coord, float(octaves), 0.5);
}


#endif // PROCEDURAL_FRACTAL_NOISE_GLSL
