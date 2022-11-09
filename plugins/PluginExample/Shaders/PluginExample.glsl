#include "Common.glsl"
#include "Common/Hash.glsl"

vec4 instance_random_color()
{
    return hash(ID[0]);
}
