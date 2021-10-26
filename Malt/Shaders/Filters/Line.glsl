//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifndef LINE_GLSL
#define LINE_GLSL

#define LINE_DEPTH_MODE_NEAR 0
#define LINE_DEPTH_MODE_FAR  1
#define LINE_DEPTH_MODE_ANY  2

#define LINE_QUALITY_MODE_PREVIEW 0
#define LINE_QUALITY_MODE_RENDER  1

void _sampling_pattern(out vec2 samples[4])
{
    samples = vec2[4](
        vec2(-1,-1),
        vec2(-1,1),
        vec2(1,-1),
        vec2(1,1)
    );

    samples = vec2[4](
        vec2(-1, 0),
        vec2( 1, 0),
        vec2( 0,-1),
        vec2( 0, 1)
    );
}

bool line_id_ex(sampler2D depth_texture, int depth_channel, usampler2D id_texture, int id_channel, vec2 uv, float pixel_width, int LINE_DEPTH_MODE)
{
    vec2 offsets[4];
    _sampling_pattern(offsets);

    vec2 offset = vec2(pixel_width) / vec2(textureSize(id_texture, 0));
    uint id = texture(id_texture, uv)[id_channel];
    float depth = texture(depth_texture, uv)[depth_channel];
    bool line = false;

    for(int i = 0; i < offsets.length(); i++)
    {   
        uint sampled_id = texture(id_texture, uv + offsets[i]*offset)[id_channel];
        float sampled_depth = texture(depth_texture, uv + offsets[i]*offset)[depth_channel];

        if(sampled_id != id)
        {
            if
            (
                LINE_DEPTH_MODE == LINE_DEPTH_MODE_ANY ||
                LINE_DEPTH_MODE == LINE_DEPTH_MODE_NEAR && depth < sampled_depth ||
                LINE_DEPTH_MODE == LINE_DEPTH_MODE_FAR && depth > sampled_depth
            )
            {
                line = true;
            }
        }
    }

    return line;
}

float line_normal_ex(sampler2D depth_texture, int depth_channel, sampler2D normal_texture, vec2 uv, float pixel_width, int LINE_DEPTH_MODE)
{
    vec2 offsets[4];
    _sampling_pattern(offsets);

    vec2 offset = vec2(pixel_width) / vec2(textureSize(normal_texture, 0));
    vec3 normal = texture(normal_texture, uv).xyz;
    float depth = texture(depth_texture, uv)[depth_channel];
    float _dot = 1.0;

    for(int i = 0; i < offsets.length(); i++)
    {   
        vec3 sampled_normal = texture(normal_texture, uv + offsets[i]*offset).xyz;
        float sampled_depth = texture(depth_texture, uv + offsets[i]*offset)[depth_channel];

        if
        (
            LINE_DEPTH_MODE == LINE_DEPTH_MODE_ANY ||
            LINE_DEPTH_MODE == LINE_DEPTH_MODE_NEAR && depth < sampled_depth ||
            LINE_DEPTH_MODE == LINE_DEPTH_MODE_FAR && depth > sampled_depth
        )
        {
            _dot = min(_dot, dot(normal, sampled_normal));
        }
    }

    return _dot;
}

float line_depth_ex(sampler2D depth_texture, int channel, vec2 uv, float pixel_width, int LINE_DEPTH_MODE)
{
    vec2 offsets[4];
    _sampling_pattern(offsets);

    vec2 offset = vec2(pixel_width) / vec2(textureSize(depth_texture, 0));
    float depth = texture(depth_texture, uv)[channel];
    depth = -depth_to_z(depth);
    float delta = 0.0;

    for(int i = 0; i < offsets.length(); i++)
    {   
        float sampled_depth = texture(depth_texture, uv + offsets[i]*offset)[channel];
        sampled_depth = -depth_to_z(sampled_depth);

        if
        (
            LINE_DEPTH_MODE == LINE_DEPTH_MODE_ANY ||
            LINE_DEPTH_MODE == LINE_DEPTH_MODE_NEAR && depth < sampled_depth ||
            LINE_DEPTH_MODE == LINE_DEPTH_MODE_FAR && depth > sampled_depth
        )
        {
            delta = max(delta, abs(depth - sampled_depth));
        }
    }

    return delta;
}

struct LineOutput
{
    float delta_distance;
    float delta_angle;
    bvec4 id_boundary;
};

LineOutput line_ex(
    vec3 position,
    vec3 normal,
    vec3 true_normal,
    float line_width,
    int line_steps,
    int LINE_DEPTH_MODE,
    vec2 uv,
    sampler2D depth_texture,
    int depth_channel,
    sampler2D normal_texture,
    usampler2D id_texture
)
{
    LineOutput result;
    result.delta_distance = 0.0;
    result.delta_angle = 1.0;
    result.id_boundary = bvec4(false);

    vec2 offsets[4];
    _sampling_pattern(offsets);
    vec2 offset = vec2(line_width) / RESOLUTION;

    vec3 true_normal_camera = transform_normal(CAMERA, true_normal);
    float depth = texture(depth_texture, uv)[depth_channel];
    position = transform_point(CAMERA, position);
    uvec4 id = texture(id_texture, uv);

    for(int i = 0; i < offsets.length(); i++)
    {   
        for(int s = 1; s <= line_steps; s++)
        {
            vec2 sample_uv = uv + offsets[i]*offset*(float(s)/float(line_steps));

            vec3 sampled_normal = texture(normal_texture, sample_uv).xyz;
            float sampled_depth = texture(depth_texture, sample_uv)[depth_channel];
            vec3 sampled_position = screen_to_camera(sample_uv, sampled_depth);
            uvec4 sampled_id = texture(id_texture, sample_uv);

            float delta_distance = 0;

            if(is_ortho(PROJECTION))
            {
                //TODO: Use ray-plane intersection here too.
                delta_distance = abs(sampled_position.z - position.z);
                delta_distance *= dot(true_normal, view_direction());
            }
            else
            {
                vec3 ray_origin = vec3(0);
                vec3 ray_direction = normalize(sampled_position);

                //TODO: Improve numerical stability
                //Sometimes the normal is almost perpendicular to the camera so expected distance is very high
                float expected_distance = ray_plane_intersection
                (
                    ray_origin, ray_direction,
                    position, true_normal_camera
                );

                delta_distance = abs(distance(sampled_position, ray_origin) - expected_distance);
            }

            if
            (
                LINE_DEPTH_MODE == LINE_DEPTH_MODE_ANY ||
                LINE_DEPTH_MODE == LINE_DEPTH_MODE_NEAR && depth < sampled_depth ||
                LINE_DEPTH_MODE == LINE_DEPTH_MODE_FAR && depth > sampled_depth
            )
            {
                result.delta_distance = max(result.delta_distance, delta_distance);
                result.delta_angle = min(result.delta_angle, dot(normal, sampled_normal));
                for(int i = 0; i < 4; i++)
                {
                    result.id_boundary[i] = result.id_boundary[i] || sampled_id[i] != id[i];
                }
            }
        }
    }

    result.delta_angle = acos(result.delta_angle);

    return result;
}


struct LineExpandOutput
{
    vec4 color;
    float depth;
};

LineExpandOutput line_expand(vec2 uv, int max_width, float aa_offset, 
                             sampler2D line_color_texture, sampler2D line_width_texture, int line_width_channel,
                             sampler2D depth_texture, int depth_channel, usampler2D id_texture, int id_channel)
{
    vec2 resolution = vec2(textureSize(line_color_texture,0));

    int max_half_width = max_width;

    float depth = texture(depth_texture, uv)[depth_channel];
    uint id = texture(id_texture, uv)[id_channel];

    vec4 line_color = vec4(0);
    float line_depth = 1.0;

    for(int x = -max_half_width; x <= max_half_width; x++)
    {
        for(int y = -max_half_width; y <= max_half_width; y++)
        {
            vec2 offset = vec2(x,y);
            float offset_length = length(offset);
            vec2 offset_uv = uv + offset / resolution;

            float offset_width = texture(line_width_texture, offset_uv)[line_width_channel];

            if(offset_width > 0 && offset_length <= offset_width / 2.0)
            {
                vec4 offset_line_color = texture(line_color_texture, offset_uv);
                float offset_line_depth = texture(depth_texture, offset_uv)[depth_channel];
                uint offset_line_id = texture(id_texture, offset_uv)[id_channel];
                
                float alpha = clamp(offset_width / 2.0 - offset_length + aa_offset, 0.0, 1.0);

                bool override = false;

                if (alpha == 1.0 && offset_line_depth < line_depth)
                {
                    override = true;
                }
                else if(alpha > line_color.a)
                {
                    override = true;
                }

                if(offset_line_id != id && depth < offset_line_depth)
                {
                    override = false;
                }

                if(override)
                {
                    line_color = offset_line_color;
                    line_color.a *= alpha;
                    line_depth = offset_line_depth;
                }
            }
        }
    }
    
    return LineExpandOutput(line_color, line_depth);
}

#endif //LINE_GLSL

