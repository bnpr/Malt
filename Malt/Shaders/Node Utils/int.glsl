#ifndef INT_GLSL
#define INT_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Int;
*/

int int_add(int a, int b){ return a+b; }
int int_subtract(int a, int b){ return a-b; }
int int_multiply(int a, int b){ return a*b; }
int int_divide(int a, int b){ return a/b; }
int int_modulo(int a, int b){ return a%b; }

int int_clamp(int i, int min, int max){ return clamp(i, min, max); }

int int_sign(int i){ return sign(i); }
int int_abs(int i){ return abs(i); }
int int_min(int a, int b){ return min(a,b); }
int int_max(int a, int b){ return max(a,b); }

bool int_equal(int a, int b){ return a == b; }
bool int_not_equal(int a, int b){ return a != b; }
bool int_greater(int a, int b){ return a > b; }
bool int_greater_or_equal(int a, int b){ return a >= b; }
bool int_less(int a, int b){ return a < b; }
bool int_less_or_equal(int a, int b){ return a <= b; }

int int_if_else(bool condition, int if_true, int if_false){ return condition ? if_true : if_false; }

#endif //INT_GLSL
