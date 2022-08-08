#ifndef INT_GLSL
#define INT_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Integer;
*/

/*META @meta: label=Add;*/
int int_add(int a, int b){ return a+b; }
/*META @meta: label=Subtract;*/
int int_subtract(int a, int b){ return a-b; }
/*META @meta: label=Multiply;*/
int int_multiply(int a, int b){ return a*b; }
/*META @meta: label=Divide;*/
int int_divide(int a, int b){ return a/b; }
/*META @meta: label=Modulo;*/
int int_modulo(int a, int b){ return a%b; }

/*META @meta: label=Clamp; @b: label=Min; @c: label=Max; */
int int_clamp(int a, int b, int c){ return clamp(a, b, c); }

/*META @meta: label=Sign;*/
int int_sign(int a){ return sign(a); }
/*META @meta: label=Absolute;*/
int int_abs(int a){ return abs(a); }
/*META @meta: label=Minimum;*/
int int_min(int a, int b){ return min(a,b); }
/*META @meta: label=Maximum;*/
int int_max(int a, int b){ return max(a,b); }

/*META @meta: label=Equal;*/
bool int_equal(int a, int b){ return a == b; }
/*META @meta: label=Not Equal;*/
bool int_not_equal(int a, int b){ return a != b; }
/*META @meta: label=Greater;*/
bool int_greater(int a, int b){ return a > b; }
/*META @meta: label=Greater or Equal;*/
bool int_greater_or_equal(int a, int b){ return a >= b; }
/*META @meta: label=Less;*/
bool int_less(int a, int b){ return a < b; }
/*META @meta: label=Less or Equal;*/
bool int_less_or_equal(int a, int b){ return a <= b; }

/*META @meta: label=If Else; @a: label=If True; @b: label=If False; */
int int_if_else(bool condition, int a, int b){ return condition ? a : b; }

#endif //INT_GLSL
