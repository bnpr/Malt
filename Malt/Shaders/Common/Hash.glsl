#ifndef COMMON_HASH_GLSL
#define COMMON_HASH_GLSL

/*  META GLOBAL
    @meta: category=Math;
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

/*  META
    @v:subtype=Data;
*/
vec4 _pcg4d(vec4 v)
{
    uvec4 u = _pcg4d(floatBitsToUint(v));
    return vec4(u) / float(0xffffffffU);
}

/*  META
    @meta: subcategory=Hash;
*/
vec4 hash(float v){ return _pcg4d(vec4(v,0,0,0)); }
/*  META
    @meta: subcategory=Hash;
*/
vec4 hash(vec2  v){ return _pcg4d(vec4(v,0,0)); }
/*  META
    @meta: subcategory=Hash;
    @v:subtype=Data;
*/
vec4 hash(vec3  v){ return _pcg4d(vec4(v,0)); }
/*  META
    @meta: subcategory=Hash;
    @v:subtype=Data;
*/
vec4 hash(vec4  v){ return _pcg4d(v); }

#endif // COMMON_HASH_GLSL
