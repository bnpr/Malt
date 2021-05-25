// int 
int int_property(int i) { return i; }

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

int int_if_else(bool condition, int a, int b){ return condition ? a : b; }

int int_from_float(float f) { return int(f); }

