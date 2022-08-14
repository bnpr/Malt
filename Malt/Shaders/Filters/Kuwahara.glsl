#ifndef KUWAHARA_GLSL
#define KUWAHARA_GLSL

/* META GLOBAL
    @meta: category=Filter; subcategory=Kuwahara;
*/

/*  META
    @meta: label=Isotropic;
    @tex: label=Texture;
    @uv: default = UV[0]; label=UV;
    @size: default=5; min=0;
*/
vec4 kuwahara(sampler2D tex, vec2 uv, int size)
{
    if(size <= 0)
    {
        return texture(tex, uv);
    }
    vec3 mean[4] = vec3[](vec3(0), vec3(0), vec3(0), vec3(0));
    vec3 sigma[4] = vec3[](vec3(0), vec3(0), vec3(0), vec3(0));

    vec2 offsets[4] = vec2[]
        (
            vec2(-size, -size), 
            vec2(-size, 0),
            vec2(0, -size),
            vec2(0, 0)
        );
    
    vec3 color;
    vec2 texel = 1.0 / textureSize(tex, 0);

    float sigma_f;
    float minimum = 99.0;

    for(int i = 0; i < 4; i++)
    {
        float total_weight = 0.0;
        for(int u = 0; u <= ceil(size); u++)
        {
            for(int v = 0; v <= ceil(size); v++)
            {
                vec2 offset = (vec2(u,v) + offsets[i]) * texel;
                float weight = max(0, 1.0 - length(offset / texel) / float(size));
                
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

/* META
    @meta: label=Anisotropic;
    @tex: label=Texture;
    @uv: label=UV; default=UV[0];
    @direction: default='vec2(0.0, 0.0)';
    @size: default=2.0; min=0.0;
    @samples: default=50; min=0;
*/
vec4 anisotropic_kuwahara(sampler2D tex, vec2 uv, vec2 direction, float size, int samples)
{
    if(size <= 0.0 || samples <= 0)
    {
        return texture(tex, uv);
    }

    vec2 texel = 1.0 / textureSize(tex, 0);

    float a = atan(direction.y, direction.x);
    mat2 rot_mat = mat2(cos(a), -sin(a), sin(a), cos(a));

    int segments = 8;
    vec3 mean[8] = vec3[](vec3(0.0),vec3(0.0),vec3(0.0),vec3(0.0),vec3(0.0),vec3(0.0),vec3(0.0),vec3(0.0));
    vec3 sigma[8] = vec3[](vec3(0.0),vec3(0.0),vec3(0.0),vec3(0.0),vec3(0.0),vec3(0.0),vec3(0.0),vec3(0.0));
    float total_weights[8] = float[](0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);

    for(int i = 0; i < samples; i++)
    {
        vec2 offset = phyllotaxis_disk(float(i), samples);
        float l = length(offset);
        float rad = atan(offset.y, offset.x) / (2.0 * PI) + 0.5;
        int segment_index = int(floor(rad * segments));
        float weight = exp(-(l * l) * 2.0);
        offset *= size * texel;
        offset.x *= length(direction) + 1.0;
        offset = rot_mat * offset;

        vec3 color = texture(tex, uv + offset).rgb;
        mean[segment_index] += color * weight;
        sigma[segment_index] += (color * color) * weight;
        total_weights[segment_index] += weight;
    }

    float sigma_f;
    float minimum = 99.0;
    vec3 result;

    for(int i = 0; i < segments; i++)
    {
        mean[i] /= total_weights[i];
        sigma[i] = abs(sigma[i] / total_weights[i] - mean[i] * mean[i]);

        sigma_f = sigma[i].r + sigma[i].g + sigma[i].b;
        if(sigma_f < minimum)
        {
            minimum = sigma_f;
            result = mean[i];
        }
    }
    return vec4(result, texture(tex, uv).a);
}

#endif //KUWAHARA_GLSL
