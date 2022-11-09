#ifndef STRUCTURE_TENSOR_GLSL
#define STRUCTURE_TENSOR_GLSL

// Described in: https://en.wikipedia.org/wiki/Structure_tensor

/* META
    @meta: category=Filter; internal=true;
    @uv: default=UV[0];
*/
vec3 structure_tensor(sampler2D tex, vec2 uv)
{
    vec2 texel = 1.0 / textureSize(tex, 0);

    // Stores the texel offset in x,y and the weight in z. the cells with weight 0 are ignored. 
    // Notice that for v, the axes of the kernel are flipped to effectively rotate the kernel.
    //   -1  0  1
    //   -2  0  2
    //   -1  0  1
    vec3 sobel_kernel[6] = vec3[](
        vec3(-1, -1, -1), vec3(+1, -1, +1),
        vec3(-1, +0, -2), vec3(+1, +0, +2),
        vec3(-1, +1, -1), vec3(+1, -1, +1)
    );

    vec3 u = vec3(0.0);
    vec3 v = vec3(0.0);
    for(int i = 0; i < 6; i++)
    {
        vec3 k = sobel_kernel[i];
        u += texture(tex, uv + texel * k.xy).xyz * k.z;
        v += texture(tex, uv + texel * k.yx).xyz * k.z;
    }
    u /= 4.0;
    v /= 4.0;
    
    return vec3(
        dot(u, u),
        dot(v, v),
        dot(u, v)
    );
}

/* META @meta: internal=true; */
vec3 flow_from_structure(vec3 s)
{
    float l = 0.5 * (s.y + s.x +sqrt(s.y*s.y - 2.0*s.x*s.y + s.x*s.x + 4.0*s.z*s.z));
    vec2 d = vec2(s.x - l, s.z);
    return (length(d) > 0.0)? vec3(normalize(d), sqrt(l)) : vec3(0,1,0);
}

#endif //STRUCTURE_TENSOR_GLSL
