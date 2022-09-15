#ifndef NODE_UTILS_2_MAT4_GLSL
#define NODE_UTILS_2_MAT4_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Matrix;
*/

/*  META
    @meta: label=Inverse;
    @a: label=Matrix; default=mat4(1);
*/
mat4 Mat4_inverse(mat4 a)
{
    return inverse(a);
}

/*  META
    @meta: label=Multiply;
    @a: default=mat4(1);
    @b: default=mat4(1);
*/
mat4 Mat4_multiply(mat4 a, mat4 b)
{
    return a * b;
}

#endif //NODE_UTILS_2_MAT4_GLSL
