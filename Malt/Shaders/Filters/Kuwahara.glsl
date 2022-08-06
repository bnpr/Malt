#ifndef KUWAHARA_GLSL
#define KUWAHARA_GLSL

/* META
    @meta: category=Filter;
    @uv: default = UV[0]; label=UV;
    @radius: default=5; min=0;
*/
vec4 kuwahara(sampler2D tex, vec2 uv, float radius, bool weighted)
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
    
    vec3 color;
    vec2 texel = 1.0 / textureSize(tex, 0);

    float sigma_f;
    float minimum = 99.0;

    for(int i = 0; i < 4; i++)
    {
        float total_weight = 0.0;
        for(int u = 0; u <= ceil(radius); u++)
        {
            for(int v = 0; v <= ceil(radius); v++)
            {
                vec2 offset = (vec2(u,v) + offsets[i]) * texel;
                float weight = 1.0;
                if(weighted){
                    weight = max(0, 1.0 - length(offset / texel) / float(radius));
                }
                
                color = texture(tex, uv + offset).rgb;
                mean[i] += color * weight;
                sigma[i] += (color * color) * weight;
                total_weight += weight;
            }
        }
        mean[i] /= total_weight;
        sigma[i] = abs(sigma[i] / total_weight - mean[i] * mean[i]);
    }

    
    for(int i = 0; i < 4; i++)
    {
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
