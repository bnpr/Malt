#ifndef NODE_UTILS_2_INT_GLSL
#define NODE_UTILS_2_INT_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Integer;
*/

/*META @meta: label=Add;*/
int Int_add(int a, int b){ return a+b; }
/*META @meta: label=Subtract;*/
int Int_subtract(int a, int b){ return a-b; }
/*META @meta: label=Multiply;*/
int Int_multiply(int a, int b){ return a*b; }
/*META @meta: label=Divide;*/
int Int_divide(int a, int b){ return a/b; }
/*META @meta: label=Modulo;*/
int Int_modulo(int a, int b){ return a%b; }

/*META @meta: label=Clamp; @b: label=Min; @c: label=Max; */
int Int_clamp(int a, int b, int c){ return clamp(a, b, c); }

/*META @meta: label=Sign;*/
int Int_sign(int a){ return sign(a); }
/*META @meta: label=Absolute;*/
int Int_abs(int a){ return abs(a); }
/*META @meta: label=Minimum;*/
int Int_min(int a, int b){ return min(a,b); }
/*META @meta: label=Maximum;*/
int Int_max(int a, int b){ return max(a,b); }

/*META @meta: label=Equal;*/
bool Int_equal(int a, int b){ return a == b; }
/*META @meta: label=Not Equal;*/
bool Int_not_equal(int a, int b){ return a != b; }
/*META @meta: label=Greater;*/
bool Int_greater(int a, int b){ return a > b; }
/*META @meta: label=Greater or Equal;*/
bool Int_greater_or_equal(int a, int b){ return a >= b; }
/*META @meta: label=Less;*/
bool Int_less(int a, int b){ return a < b; }
/*META @meta: label=Less or Equal;*/
bool Int_less_or_equal(int a, int b){ return a <= b; }

/*META @meta: label=If Else; @a: label=If True; @b: label=If False; */
int Int_if_else(bool condition, int a, int b){ return condition ? a : b; }

#endif //NODE_UTILS_2_INT_GLSL
