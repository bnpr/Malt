#ifndef COMMON_HASH_GLSL
#define COMMON_HASH_GLSL

/*  META GLOBAL
    @meta: category=Math; internal=True;
*/

uvec4 _pcg4d(uvec4 v)
{
    //http://www.jcgt.org/published/0009/03/02/
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

vec4 _pcg4d(vec4 v)
{
    uvec4 u = _pcg4d(floatBitsToUint(v));
    return vec4(u) / float(0xffffffffU);
}

vec4 hash(float v){ return _pcg4d(vec4(v,0,0,0)); }
vec4 hash(vec2  v){ return _pcg4d(vec4(v,0,0)); }
vec4 hash(vec3  v){ return _pcg4d(vec4(v,0)); }
/* META @meta: internal=false; @v:subtype=Data; */
vec4 hash(vec4  v){ return _pcg4d(v); }

#endif // COMMON_HASH_GLSL
