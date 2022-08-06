#ifndef STRUCTURE_TENSOR_GLSL
#define STRUCTURE_TENSOR_GLSL

// Described in: https://en.wikipedia.org/wiki/Structure_tensor
// Based on: https://www.shadertoy.com/view/tssfDB


/* META
    @meta: category=Filter; internal=true;
    @uv: default=UV[0];
*/
vec3 structure_tensor(sampler2D tex, vec2 uv)
{
    vec2 texel = 1.0 / textureSize(tex, 0);

    vec3 u = (
        - 1.0 * texture(tex, uv + vec2(-texel.x, -texel.y)).xyz
        - 2.0 * texture(tex, uv + vec2(-texel.x, 0.0)).xyz
        - 1.0 * texture(tex, uv + vec2(-texel.x, texel.y)).xyz
        + 1.0 * texture(tex, uv + vec2(texel.x, -texel.y)).xyz
        + 2.0 * texture(tex, uv + vec2(texel.x, 0.0)).xyz
        + 1.0 * texture(tex, uv + vec2(texel.x, texel.y)).xyz
        ) / 4.0;

    vec3 v = (
        - 1.0 * texture(tex, uv + vec2(-texel.x, -texel.y)).xyz
        - 2.0 * texture(tex, uv + vec2(0.0, -texel.y)).xyz
        - 1.0 * texture(tex, uv + vec2(texel.x, -texel.y)).xyz
        + 1.0 * texture(tex, uv + vec2(-texel.x, texel.y)).xyz
        + 2.0 * texture(tex, uv + vec2(0.0, texel.y)).xyz
        + 1.0 * texture(tex, uv + vec2(texel.x, texel.y)).xyz
        ) / 4.0;
    
    return vec3(
        dot(u, u),
        dot(v, v),
        dot(u, v)
    );
}

#endif //STRUCTURE_TENSOR_GLSL