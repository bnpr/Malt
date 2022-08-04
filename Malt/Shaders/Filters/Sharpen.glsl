#ifndef SHARPEN_GLSL
#define SHARPEN_GLSL

/* META
    @meta: category=Filter;
    @uv: default = UV[0];
    @sharpness: default = 0.1; min=0.0;
*/
vec4 sharpen(sampler2D tex, vec2 uv, float sharpness)
{
    vec4 base = texture(tex, uv);
    if(sharpness <= 0.0){ return base; }

    vec2 tex_size = textureSize(tex, 0);
    vec3 neighbors;

    vec2 offsets[4] = vec2[]( vec2(0, 1), vec2(0, -1), vec2(1, 0), vec2(-1, 0));
    for(int i = 0; i < 4; ++i)
    {
        neighbors += texture(tex, uv + offsets[i] / tex_size).rgb * vec3(-sharpness);
    }
    base.rgb += (base.rgb * vec3(sharpness * 4)) + neighbors;
    return base;
}

#endif //SHARPEN_GLSL