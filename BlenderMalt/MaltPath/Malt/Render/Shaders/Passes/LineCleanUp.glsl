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

uniform sampler2D line_data_texture;

layout (location = 0) out vec4 OUT_RESULT;

void main()
{
    vec2 uv = screen_uv();
    vec2 resolution = vec2(textureSize(line_data_texture,0));

    vec4 line_data = texture(line_data_texture, uv);

    int half_width = 5;

    if(line_data.z >= 0)
    {
        for(int x = -half_width; x <= half_width; x++)
        {
            for(int y = -half_width; y <= half_width; y++)
            {
                vec2 offset_uv = uv + (vec2(x,y) / resolution);
                vec4 offset_line_data = texture(line_data_texture, offset_uv);

                if(offset_line_data.z >= 0 && offset_line_data.z < line_data.z)
                {
                    line_data.z = offset_line_data.z;
                }
            }
        }
    }

    OUT_RESULT = line_data;
}

#endif //PIXEL_SHADER
