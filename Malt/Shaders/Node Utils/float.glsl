#ifndef FLOAT_GLSL
#define FLOAT_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Float;
*/

float float_add(float a, float b){ return a+b; }
float float_subtract(float a, float b){ return a-b; }
float float_multiply(float a, float b){ return a*b; }
float float_divide(float a, float b){ return a/b; }
float float_modulo(float a, float b){ return mod(a,b); }
float float_pow(float f, float e){ return pow(f, e); }
float float_sqrt(float f){ return sqrt(f); }

float float_round(float f){ return round(f); }
float float_fract(float f){ return fract(f); }
float float_floor(float f){ return floor(f); }
float float_ceil(float f){ return ceil(f); }

float float_clamp(float f, float min, float max){ return clamp(f, min, max); }

float float_sign(float f){ return sign(f); }
float float_abs(float f){ return abs(f); }
float float_min(float a, float b){ return min(a,b); }
float float_max(float a, float b){ return max(a,b); }

float float_mix(float a, float b, float factor){ return mix(a,b,factor); }

float float_sin(float f) { return sin(f); }
float float_cos(float f) { return cos(f); }
float float_tan(float f) { return tan(f); }
float float_asin(float f) { return asin(f); }
float float_acos(float f) { return acos(f); }
float float_atan(float f) { return atan(f); }

float float_degrees(float r) { return degrees(r); }
float float_radians(float d) { return radians(d); }

bool float_equal(float a, float b){ return a == b; }
bool float_not_equal(float a, float b){ return a != b; }
bool float_greater(float a, float b){ return a > b; }
bool float_greater_or_equal(float a, float b){ return a >= b; }
bool float_less(float a, float b){ return a < b; }
bool float_less_or_equal(float a, float b){ return a <= b; }

float float_if_else(bool condition, float if_true, float if_false){ return condition ? if_true : if_false; }

#endif //FLOAT_GLSL
