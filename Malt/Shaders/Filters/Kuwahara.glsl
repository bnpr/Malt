#ifndef KUWAHARA_GLSL
#define KUWAHARA_GLSL

/* META
    @meta: category=Filter;
    @uv: default = UV[0]; label=UV;
    @radius: default=5; min=0;
*/
vec4 kuwahara_sampling(sampler2D tex, vec2 uv, int radius)
{
    if(radius <= 0)
    {
        return texture(tex, uv);
    }
    vec3 mean[4] = vec3[](vec3(0), vec3(0), vec3(0), vec3(0));
    vec3 sigma[4] = vec3[](vec3(0), vec3(0), vec3(0), vec3(0));

    vec2 offsets[4] = vec2[]
        (
            vec2(-radius, -radius), 
            vec2(-radius, 0),
            vec2(0, -radius),
            vec2(0, 0)
        );
    
    vec2 pos;
    vec3 color;
    vec2 texel = 1.0 / textureSize(tex, 0);

    float sample_count = pow(radius + 1, 2);
    float sigma_f;
    float minimum = 99.0;

    for(int i = 0; i < 4; i++)
    {
        for(int u = 0; u <= radius; u++)
        {
            for(int v = 0; v <= radius; v++)
            {
                pos = (vec2(u,v) + offsets[i]) * texel;
                color = texture(tex, uv + pos).rgb;
                mean[i] += color;
                sigma[i] += color * color;
            }
        }
    }
    
    for(int i = 0; i < 4; i++)
    {
        mean[i] /= sample_count;
        sigma[i] = abs(sigma[i] / sample_count - mean[i] * mean[i]);
        sigma_f = sigma[i].r + sigma[i].g + sigma[i].b;
        if(sigma_f < minimum)
        {
            minimum = sigma_f;
            color = mean[i];
        }
    }
    return vec4(color, texture(tex, uv).a);
}

#endif //KUWAHARA_GLSL
