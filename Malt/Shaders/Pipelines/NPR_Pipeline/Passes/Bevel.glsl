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

#define BEVEL_ID_SAMPLER usampler2D

#define BEVEL_FETCH_ID(texture, texel, channel) int(bitfieldExtract(texelFetch(texture, texel, 0)[channel], 8, 8));

#include "Filters/Bevel.glsl"

uniform sampler2D IN_NORMAL_DEPTH;
uniform usampler2D IN_BEVEL_DATA;

layout (location = 0) out vec4 OUT_RESULT;

void main()
{
    vec4 normal_depth = texture(IN_NORMAL_DEPTH, UV[0]);
    vec3 normal = normal_depth.xyz;
    float depth = normal_depth.w;
    vec3 position = screen_to_camera(UV[0], depth);
    position = transform_point(inverse(CAMERA), position);

    uvec4 packed_data = texture(IN_BEVEL_DATA, UV[0]);
    
    vec2 radius_distribution = unpackHalf2x16(packed_data.x);
    float radius = radius_distribution.x;
    float distribution_exponent = radius_distribution.y;
    
    uint samples = bitfieldExtract(packed_data.y, 0, 8);
    uint bevel_group = bitfieldExtract(packed_data.y, 8, 8);
    bool hard_mode = bitfieldExtract(packed_data.y, 16, 8) == 1;
    float hard_mode_max_dot = unpackSnorm4x8(bitfieldExtract(packed_data.y, 24, 8)).w;

    OUT_RESULT = normal_depth;
    if(samples > 0 && radius > 0)
    {
        OUT_RESULT.xyz = bevel_ex(
            IN_NORMAL_DEPTH, IN_NORMAL_DEPTH, 3,
            int(bevel_group), true, IN_BEVEL_DATA, 1,
            int(samples), radius, distribution_exponent,
            hard_mode, hard_mode_max_dot
        );
    }
}

#endif //PIXEL_SHADER
