//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Common.glsl"

#ifdef VERTEX_SHADER
void main()
{
    POSITION = in_position;
    UV[0] = in_position.xy * 0.5 + 0.5;

    gl_Position = vec4(POSITION, 1);
}
#endif

#ifdef PIXEL_SHADER

uniform sampler2D color_texture;
uniform sampler2D depth_texture;
uniform sampler2D id_texture;
uniform sampler2D line_color_texture;
uniform sampler2D line_data_texture;
uniform sampler2D line_distance_field_texture;
uniform float aa_offset = 0.0;

layout (location = 0) out vec4 OUT_RESULT;

#define BASIC_COMPOSITE 1
#define ADVANCED_COMPOSITE 2
#define BRUTE_FORCE 3

//TODO: Use brute force on closer range and fallback to distance fields for wider lines
#define LINE_MODE BRUTE_FORCE

bool line_is_in_range(float depth_a, float depth_b, float width)
{
    width = pixel_world_size_at(depth_a) * width;
    depth_a = depth_to_z(depth_a);
    depth_b = depth_to_z(depth_b);

    return abs(depth_a - depth_b) <= width;
}

#if LINE_MODE == BASIC_COMPOSITE

void main()
{
    vec2 uv = screen_uv();
    vec2 resolution = vec2(textureSize(line_color_texture,0));
    
    vec4 line_distance_field = texture(line_distance_field_texture, uv);
    vec2 line_uv = line_distance_field.xy;
    float line_width = line_distance_field.z;
    float line_delta = distance(uv * resolution, line_uv * resolution);
    
    vec4 line_color = texture(line_color_texture, line_uv);
    vec4 color = texture(color_texture, uv);
    
    float line_alpha = clamp(line_width / 2.0 - line_delta + aa_offset, 0.0, 1.0);

    OUT_RESULT = mix(color, line_color, line_alpha);
}

#elif LINE_MODE == ADVANCED_COMPOSITE

void main()
{
    vec2 uv = screen_uv();
    vec2 resolution = vec2(textureSize(line_color_texture,0));
    
    vec4 line_distance_field = texture(line_distance_field_texture, uv);
    vec2 line_uv = line_distance_field.xy;
    float line_width = line_distance_field.z;
    float line_delta = distance(uv * resolution, line_uv * resolution);
        
    float line_depth = texture(depth_texture, line_uv).x;

    float override_normalized_delta = 1.0;

    if(line_delta <= line_width / 2.0)
    {
        // Here we are doing depth testing, basically. Since line selection is done with distance fields,
        // sometimes the nearest (in pixels) line is not the line we should render since
        // we could have another line closer to the camera.

        int max_width = int(ceil(line_width / 2.0));
        
        for(int x = -max_width; x <= max_width; x++)
        {
            for(int y = -max_width; y <= max_width; y++)
            {
                vec2 offset = vec2(x,y);
                float offset_length = length(offset);
                vec2 offset_uv = uv + offset / resolution;

                vec4 offset_line_data = texture(line_data_texture, offset_uv);
                float offset_width = offset_line_data.z;

                if(offset_width > 0 && offset_length <= offset_width / 2.0)
                {
                    float offset_line_depth = texture(depth_texture, offset_uv).x;
                    vec4 offset_line_color = texture(line_color_texture, offset_uv);
                    
                    //TODO: do something better. (Sphere ray casting ???)
                    float line_range = line_width * 2.0;

                    if(offset_line_depth < line_depth && !line_is_in_range(line_depth, offset_line_depth, line_range))
                    {
                        float normalized_delta = offset_length / (offset_width / 2.0);
                        float override_alpha = clamp(offset_width / 2.0 - offset_length + aa_offset, 0.0, 1.0);

                        //Override only if alpha equals to 1, otherwise we get transparent line pixels at intersections
                        if(normalized_delta < override_normalized_delta && override_alpha >= 1.0)
                        {
                            override_normalized_delta = normalized_delta;
                            line_uv = offset_uv;
                            line_width = offset_width;
                        }
                    }
                }
            }
        }
    }

    vec4 line_color = texture(line_color_texture, line_uv);
    vec4 color = texture(color_texture, uv);

    line_delta = distance(uv * resolution, line_uv * resolution);
    float line_alpha = clamp(line_width / 2.0 - line_delta + aa_offset, 0.0, 1.0);

    //Depth ID testing. Don't let thick lines get inside other objects!
    float id = texture(id_texture, uv).x;
    float line_id = texture(id_texture, line_uv).x;

    if(id != line_id)
    {
        float depth = texture(depth_texture, uv).x;
        line_depth = texture(depth_texture, line_uv).x;
        
        if(depth < line_depth)
        {
            line_alpha = 0;
        }
    }
    
    OUT_RESULT = mix(color, line_color, line_alpha);
}

#elif LINE_MODE == BRUTE_FORCE

uniform int brute_force_range = 10;

void main()
{
    vec2 uv = screen_uv();
    vec2 resolution = vec2(textureSize(line_color_texture,0));

    int max_half_width = brute_force_range;

    vec4 color = texture(color_texture, uv);
    float depth = texture(depth_texture, uv).x;
    float id = texture(id_texture, uv).x;

    vec4 line_color = vec4(0);
    float line_depth = 1.0;

    for(int x = -max_half_width; x <= max_half_width; x++)
    {
        for(int y = -max_half_width; y <= max_half_width; y++)
        {
            vec2 offset = vec2(x,y);
            float offset_length = length(offset);
            vec2 offset_uv = uv + offset / resolution;

            vec4 offset_line_data = texture(line_data_texture, offset_uv);
            float offset_width = offset_line_data.z;

            if(offset_width > 0 && offset_length <= offset_width / 2.0)
            {
                vec4 offset_line_color = texture(line_color_texture, offset_uv);
                float offset_line_depth = texture(depth_texture, offset_uv).x;
                float offset_line_id = texture(id_texture, offset_uv).x;
                
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
                    line_color.a = alpha;
                    line_depth = offset_line_depth;
                }
            }
        }
    }

    OUT_RESULT = mix(color, line_color, line_color.a);
}

#endif //LINE_MODE

#endif //PIXEL_SHADER
