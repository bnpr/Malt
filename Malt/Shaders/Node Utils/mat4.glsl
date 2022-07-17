#ifndef MAT4_GLSL
#define MAT4_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Mat4;
*/

/*  META
    @matrix: default=mat4(1);
*/
mat4 mat4_inverse(mat4 matrix)
{
    return inverse(matrix);
}

#endif //MAT4_GLSL
