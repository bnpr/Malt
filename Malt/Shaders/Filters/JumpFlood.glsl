#ifndef JUMP_FLOOD_GLSL
#define JUMP_FLOOD_GLSL

/*  META
    @width: default=1.0;
*/
//input should be a texture where x and y are screen space uvs.
//samples with values == vec(-1,-1) are ignored
//More info : https://medium.com/@bgolus/the-quest-for-very-wide-outlines-ba82ed442cd9#c5bb
vec4 jump_flood(sampler2D input_texture, vec2 uv, float width, bool third_channel_scale)
{
    vec4 nearest = vec4(-1,-1,-1,-1);
    vec2 resolution = vec2(textureSize(input_texture, 0));
    vec2 offset = vec2(width) / resolution;

    for(int x = -1; x <= 1; x++)
    {
        for(int y = -1; y <= 1; y++)
        {
            vec2 sample_uv = uv + vec2(x,y) * offset;
            vec4 sampled = texture(input_texture, sample_uv);
            if(sampled.xy != vec2(-1,-1)) //Check if it's valid
            {
                float stored_distance = distance(uv * resolution, nearest.xy * resolution);
                float sampled_distance = distance(uv * resolution, sampled.xy * resolution);
                
                if(third_channel_scale)
                {
                    if(nearest.z > 0)
                    {
                        stored_distance /= nearest.z;
                    }
                    if(sampled.z > 0)
                    {
                        sampled_distance /= sampled.z;
                    }
                }

                if(nearest.xy == vec2(-1,-1) || sampled_distance < stored_distance)
                {
                    nearest = sampled;
                }
            }
        }
    }

    return nearest;
}


#endif //JUMP_FLOOD_GLSL

