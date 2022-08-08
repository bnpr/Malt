#ifndef MAT4_GLSL
#define MAT4_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Matrix;
*/

/*  META
    @meta: label=Inverse;
    @a: label=Matrix; default=mat4(1);
*/
mat4 mat4_inverse(mat4 a)
{
    return inverse(a);
}

/*  META
    @meta: label=Multiply;
    @a: default=mat4(1);
    @b: default=mat4(1);
*/
mat4 mat4_multiply(mat4 a, mat4 b)
{
    return a * b;
}

#endif //MAT4_GLSL
