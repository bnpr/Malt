#ifndef LINE_GLSL
#define LINE_GLSL

#define LINE_DEPTH_MODE_NEAR 0
#define LINE_DEPTH_MODE_FAR  1
#define LINE_DEPTH_MODE_ANY  2

/* META GLOBAL
    @meta: internal=true;
*/

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

//TODO: Remove. Used by surface_curvature
float _line_detection_depth(sampler2D depth_texture, int channel, vec2 uv, float pixel_width, int LINE_DEPTH_MODE)
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

struct LineDetectionOutput
{
    float delta_distance;
    float delta_angle;
    bvec4 id_boundary;
};

/*  META
    @position: subtype=Vector; default=POSITION;
    @normal: subtype=Normal; default=NORMAL;
    @true_normal: subtype=Normal; default=true_normal();
    @width: default=1.0;
    @LINE_DEPTH_MODE: subtype=ENUM(Near, Far, Any);
    @uv: default=UV[0];
*/
LineDetectionOutput line_detection(
    vec3 position,
    vec3 normal,
    vec3 true_normal,
    float width,
    int LINE_DEPTH_MODE,
    vec2 uv,
    sampler2D depth_texture,
    int depth_channel,
    sampler2D normal_texture,
    usampler2D id_texture
)
{
    LineDetectionOutput result;
    result.delta_distance = 0.0;
    result.delta_angle = 1.0;
    result.id_boundary = bvec4(false);

    vec2 offsets[4];
    _sampling_pattern(offsets);
    vec2 offset = vec2(width) / RESOLUTION;

    vec3 true_normal_camera = transform_normal(CAMERA, true_normal);
    float depth = texture(depth_texture, uv)[depth_channel];
    position = transform_point(CAMERA, position);
    uvec4 id = texture(id_texture, uv);

    for(int i = 0; i < offsets.length(); i++)
    {   
        vec2 sample_uv = uv + offsets[i]*offset;

        vec3 sampled_normal = texture(normal_texture, sample_uv).xyz;
        float sampled_depth = texture(depth_texture, sample_uv)[depth_channel];
        vec3 sampled_position = screen_to_camera(sample_uv, sampled_depth);
        uvec4 sampled_id = texture(id_texture, sample_uv);

        float delta_distance = 0;

        if(is_ortho(PROJECTION))
        {
            //TODO: Use ray-plane intersection here too.
            delta_distance = abs(sampled_position.z - position.z);
            delta_distance *= dot(true_normal, -view_direction());
        }
        else
        {
            vec3 ray_origin = vec3(0);
            vec3 ray_direction = normalize(sampled_position);

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
            LINE_DEPTH_MODE == LINE_DEPTH_MODE_NEAR && depth <= sampled_depth ||
            LINE_DEPTH_MODE == LINE_DEPTH_MODE_FAR && depth >= sampled_depth
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

    result.delta_angle = acos(result.delta_angle);

    return result;
}


LineDetectionOutput line_detection_2(
    sampler2D depth_texture,
    int depth_channel,
    sampler2D normal_texture,
    usampler2D id_texture
)
{
    ivec2 uv = screen_pixel();

    LineDetectionOutput result;
    result.delta_distance = 0.0;
    result.delta_angle = 0.0;
    result.id_boundary = bvec4(false);

    float depth = texelFetch(depth_texture, uv, 0)[depth_channel];
    vec3 normal = texelFetch(normal_texture, uv, 0).xyz;;
    
    vec3 position = screen_to_camera(screen_uv(), depth);

    vec3 true_normal = true_normal();
    //Reconstructing the normal from depth provides more stable results across samples than the "real" true_normal
    //true_normal = reconstruct_normal(depth_texture, depth_channel, uv);

    vec3 average_normal = vec3(0);
    int radius = 1;
    for(int x = -radius; x <= radius; x++)
    {
        for(int y = -radius; y <= radius; y++)
        {
            ivec2 uv = uv + ivec2(x,y);
            if(uv != clamp(uv, ivec2(0), RESOLUTION))
            {
                continue;
            }
            vec3 n = reconstruct_normal(depth_texture, depth_channel, uv);
            average_normal += n;
        }   
    }
    true_normal = normalize(average_normal);

    uvec4 id = texelFetch(id_texture, uv, 0);
    
    vec3 true_normal_camera = transform_normal(CAMERA, true_normal);

    vec2 offsets[4]; _sampling_pattern(offsets);
    vec2 offset = vec2(1.0) / RESOLUTION;

    for(int i = 0; i < offsets.length(); i++)
    {   
        ivec2 sample_uv = uv + ivec2(offsets[i]);
        if(sample_uv != clamp(sample_uv, ivec2(0), RESOLUTION))
        {
            continue;
        }
        vec2 f_sample_uv = screen_uv() + offsets[i] * offset;

        vec3 sampled_normal = texelFetch(normal_texture, sample_uv, 0).xyz;
        float sampled_depth = texelFetch(depth_texture, sample_uv, 0)[depth_channel];
        vec3 sampled_position = screen_to_camera(f_sample_uv , sampled_depth);
        uvec4 sampled_id = texelFetch(id_texture, sample_uv, 0);

        float delta_normal = dot(true_normal, sampled_normal);
        
        float plane_distance = dot(true_normal_camera, position);
        float offset_plane_distance = dot(true_normal_camera, sampled_position);

        // Scale by pixel world size so results are more stable at different distances and resolutions
        float delta_distance = abs(plane_distance - offset_plane_distance) / pixel_world_size();

        /* Alternative depth computation
        {
            vec3 ray_origin = vec3(0);
            vec3 ray_direction = normalize(sampled_position);

            float expected_distance = ray_plane_intersection
            (
                ray_origin, ray_direction,
                position, true_normal_camera
            );
            
            delta_distance = distance(position, sampled_position) / distance(position, ray_origin + ray_direction * expected_distance);
        }
        //*/

        if(depth <= sampled_depth)
        {
            result.delta_distance = max(result.delta_distance, delta_distance);
            result.delta_angle = max(result.delta_angle, 1.0 - delta_normal);
            
            for(int i = 0; i < 4; i++)
            {
                result.id_boundary[i] = result.id_boundary[i] || sampled_id[i] != id[i];
            }
        }
    }

    return result;
}


struct LineExpandOutput
{
    vec4 color;
    float depth;
};

/*  META
    @uv: default=UV[0];
    @max_width: default=10;
*/
LineExpandOutput line_expand(vec2 uv, int max_width,
                             sampler2D line_color_texture, sampler2D line_width_texture, int line_width_channel, float line_width_scale,
                             sampler2D depth_texture, int depth_channel, usampler2D id_texture, int id_channel)
{
    vec2 resolution = vec2(textureSize(line_color_texture,0));

    int max_half_width = int(ceil(max_width / 2.0));

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

            float offset_width = texture(line_width_texture, offset_uv)[line_width_channel] * line_width_scale;
            offset_width = min(offset_width, max_width);

            if(offset_width > 0 && offset_length <= offset_width / 2.0)
            {
                vec4 offset_line_color = texture(line_color_texture, offset_uv);
                float offset_line_depth = texture(depth_texture, offset_uv)[depth_channel];
                uint offset_line_id = texture(id_texture, offset_uv)[id_channel];
                
                float alpha = clamp(offset_width / 2.0 - offset_length, 0.0, 1.0);

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

