//Copyright (c) 2021 BlenderNPR and contributors. MIT license.

#ifndef COMMON_HASH_GLSL
#define COMMON_HASH_GLSL

//pcg4d hash function.
//http://www.jcgt.org/published/0009/03/02/

uvec4 pcg4d(uvec4 v)
{
    v = v * 1664525u + 1013904223u;
    
    v.x += v.y*v.w;
    v.y += v.z*v.x;
    v.z += v.x*v.y;
    v.w += v.y*v.z;
    
    v ^= v >> 16u;
    
    v.x += v.y*v.w;
    v.y += v.z*v.x;
    v.z += v.x*v.y;
    v.w += v.y*v.z;
    
    return v;
}


//Conversion functions
//Overloaded function to convert input float, vec, or uvec to uvec4 for hash

uvec4 uv4(float s){
    uvec4 u;
    v = uvec4(uint(s), 1u, 1u, 1u);
    return v;
}

uvec4 uv4(uvec2 s){
    uvec4 u;
    u = uvec4(s, s.x ^ s.y, s.x + s.y)
    return u;
}

uvec4 uv4(uvec3 s){
    uvec4 u;
    u = uvec4(s, s.x ^ s.y);
    return u;
}

uvec4 uv4(vec2 s){
    uvec4 u;
    u = uvec4(s, uint(s.x) ^ uint(s.y), uint(s.x) + uint(s.y))
    return u;
}

uvec4 uv4(vec3 s){
    uvec4 u;
    u = uvec4(s, uint(s.x) ^ uint(s.y))
    return u;
}


//Overloaded hash functions
//Converts float, uvec, or vec into necessary input uvec4d, and hashes it.
//uhash returns uvec4, and hash returns vec4
vec4 hash(float s)
{
    vec4 u;
    vec4 v;
    u = uv4(s);
    v = vec4(pc4d(u));
    return v;
}

vec4 hash(vec2 s)
{
    vec4 u;
    vec4 v;
    u = uv4(s);
    v = vec4(pc4d(u));
    return v;
}

vec4 hash(vec3 s)
{
    vec4 u;
    vec4 v;
    u = uv4(s);
    v = vec4(pc4d(u));
    return v;
}

vec4 hash(vec4 s)
{
    vec4 u;
    vec4 v;
    u = uvec4(s);
    v = vec4(pc4d(u));
    return v;
}

vec4 hash(uvec2 s)
{
    vec4 u;
    vec4 v;
    u = uv4(s);
    v = vec4(pc4d(u));
    return v;
}

vec4 hash(uvec3 s)
{
    vec4 u;
    vec4 v;
    u = uv4(s);
    v = vec4(pc4d(u));
    return v;
}

vec4 hash(uvec4 s)
{
    vec4 v;
    v = vec4(pc4d(s));
    return v;
}

uvec4 uhash(float s)
{
    uvec4 u;
    vec4 v;
    u = uv4(s);
    v = pc4d(u);
    return v;
}

uvec4 uhash(vec2 s)
{
    uvec4 u;
    vec4 v;
    u = uv4(s);
    v = pc4d(u);
    return v;
}

uvec4 uhash(vec3 s)
{
    uvec4 u;
    vec4 v;
    u = uv4(s);
    v = pc4d(u);
    return v;
}

uvec4 uhash(vec4 s)
{
    uvec4 u;
    vec4 v;
    u = uvec4(s);
    v = pc4d(u);
    return v;
}

uvec4 uhash(uvec2 s)
{
    uvec4 u;
    vec4 v;
    u = uv4(s);
    v = pc4d(u);
    return v;
}


uvec4 uhash(uvec3 s)
{
    uvec4 u;
    vec4 v;
    u = uv4(s);
    v = pc4d(u);
    return v;
}

uvec4 uhash(uvec4 s)
{
    uvec4 v;
    v = pc4d(s);
    return v;
}

#endif // COMMON_HASH_GLSL