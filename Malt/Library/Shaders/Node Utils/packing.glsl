#ifndef PACKING_GLSL
#define PACKING_GLSL

uvec4 pack_8bit(vec4 a, vec4 b, vec4 c, vec4 d)
{
    return uvec4(packUnorm4x8(a), packUnorm4x8(b), packUnorm4x8(c), packUnorm4x8(d));
}

void unpack_8bit(uvec4 packed_vector, out vec4 a, out vec4 b, out vec4 c, out vec4 d)
{
    a = unpackUnorm4x8(packed_vector.x);
    b = unpackUnorm4x8(packed_vector.y);
    c = unpackUnorm4x8(packed_vector.z);
    d = unpackUnorm4x8(packed_vector.w);
}

#endif //PACKING_GLSL
