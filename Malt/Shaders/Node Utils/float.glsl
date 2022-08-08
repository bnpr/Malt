#ifndef FLOAT_GLSL
#define FLOAT_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Float;
*/

/*META @meta: label=Add;*/
float float_add(float a, float b){ return a+b; }
/*META @meta: label=Subtract;*/
float float_subtract(float a, float b){ return a-b; }
/*META @meta: label=Multiply;*/
float float_multiply(float a, float b){ return a*b; }
/*META @meta: label=Divide;*/
float float_divide(float a, float b){ return a/b; }
/*META 
    @meta: label=Map Range; 
    @clamped: default=true;
    @value: default = 0.5;
    @from_min: default = 0.0;
    @from_max: default = 1.0;
    @to_min: default = 0.0;
    @to_max: default = 1.0;
*/
float float_map_range(bool clamped, float value, float from_min, float from_max, float to_min, float to_max)
{
    if(clamped)
    {
        return map_range_clamped(value, from_min, from_max, to_min, to_max);
    }
    else
    {
        return map_range(value, from_min, from_max, to_min, to_max);
    }
}
/*META @meta: label=Modulo;*/
float float_modulo(float a, float b){ return mod(a,b); }
/*META @meta: label=Power;*/
float float_pow(float a, float b){ return pow(a, b); }
/*META @meta: label=Square Root;*/
float float_sqrt(float a){ return sqrt(a); }

/*META @meta: label=Round;*/
float float_round(float a){ return round(a); }
/*META @meta: label=Fractional Part;*/
float float_fract(float a){ return fract(a); }
/*META @meta: label=Floor;*/
float float_floor(float a){ return floor(a); }
/*META @meta: label=Ceil;*/
float float_ceil(float a){ return ceil(a); }

/*META @meta: label=Clamp; @b: label=Min; @c: label=Max; */
float float_clamp(float a, float b, float c){ return clamp(a, b, c); }

/*META @meta: label=Sign;*/
float float_sign(float a){ return sign(a); }
/*META @meta: label=Absolute;*/
float float_abs(float a){ return abs(a); }
/*META @meta: label=Minimum;*/
float float_min(float a, float b){ return min(a,b); }
/*META @meta: label=Maximum;*/
float float_max(float a, float b){ return max(a,b); }

/*META @meta: label=Mix;*/
float float_mix(float a, float b, float fac){ return mix(a,b,fac); }

/*META @meta: label=Sine;*/
float float_sin(float a) { return sin(a); }
/*META @meta: label=Cosine;*/
float float_cos(float a) { return cos(a); }
/*META @meta: label=Tangent;*/
float float_tan(float a) { return tan(a); }
/*META @meta: label=Arcsine;*/
float float_asin(float a) { return asin(a); }
/*META @meta: label=Arcosine;*/
float float_acos(float a) { return acos(a); }
/*META @meta: label=Arctangent;*/
float float_atan(float a) { return atan(a); }

/*META @meta: label=Radians to Degrees;*/
float float_degrees(float a) { return degrees(a); }
/*META @meta: label=Degrees to Radians;*/
float float_radians(float a) { return radians(a); }

/*META @meta: label=Equal;*/
bool float_equal(float a, float b){ return a == b; }
/*META @meta: label=Not Equal;*/
bool float_not_equal(float a, float b){ return a != b; }
/*META @meta: label=Greater;*/
bool float_greater(float a, float b){ return a > b; }
/*META @meta: label=Greater or Equal;*/
bool float_greater_or_equal(float a, float b){ return a >= b; }
/*META @meta: label=Less;*/
bool float_less(float a, float b){ return a < b; }
/*META @meta: label=Less or Equal;*/
bool float_less_or_equal(float a, float b){ return a <= b; }

/*META @meta: label=If Else; @a: label=If True; @b: label=If False; */
float float_if_else(bool condition, float a, float b){ return condition ? a : b; }

#endif //FLOAT_GLSL
