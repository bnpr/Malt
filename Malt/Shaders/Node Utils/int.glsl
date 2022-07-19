#ifndef INT_GLSL
#define INT_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Integer Math;
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

/*META @meta: label=Clamp;*/
int int_clamp(int i, int min, int max){ return clamp(i, min, max); }

/*META @meta: label=Sign;*/
int int_sign(int i){ return sign(i); }
/*META @meta: label=Absolute;*/
int int_abs(int i){ return abs(i); }
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

/*META @meta: label=If Else;*/
int int_if_else(bool condition, int if_true, int if_false){ return condition ? if_true : if_false; }

#endif //INT_GLSL
