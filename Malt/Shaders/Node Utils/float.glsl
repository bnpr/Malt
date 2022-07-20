#ifndef FLOAT_GLSL
#define FLOAT_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Float Math;
*/

/*META @meta: label=Add;*/
float float_add(float a, float b){ return a+b; }
/*META @meta: label=Subtract;*/
float float_subtract(float a, float b){ return a-b; }
/*META @meta: label=Multiply;*/
float float_multiply(float a, float b){ return a*b; }
/*META @meta: label=Divide;*/
float float_divide(float a, float b){ return a/b; }
/*META @meta: label=Modulo;*/
float float_modulo(float a, float b){ return mod(a,b); }
/*META @meta: label=Power;*/
float float_pow(float f, float e){ return pow(f, e); }
/*META @meta: label=Square Root;*/
float float_sqrt(float f){ return sqrt(f); }

/*META @meta: label=Round;*/
float float_round(float f){ return round(f); }
/*META @meta: label=Fractional Part;*/
float float_fract(float f){ return fract(f); }
/*META @meta: label=Floor;*/
float float_floor(float f){ return floor(f); }
/*META @meta: label=Ceil;*/
float float_ceil(float f){ return ceil(f); }

/*META @meta: label=Clamp;*/
float float_clamp(float f, float min, float max){ return clamp(f, min, max); }

/*META @meta: label=Sign;*/
float float_sign(float f){ return sign(f); }
/*META @meta: label=Absolute;*/
float float_abs(float f){ return abs(f); }
/*META @meta: label=Minimum;*/
float float_min(float a, float b){ return min(a,b); }
/*META @meta: label=Maximum;*/
float float_max(float a, float b){ return max(a,b); }

/*META @meta: label=Mix;*/
float float_mix(float a, float b, float factor){ return mix(a,b,factor); }

/*META @meta: label=Sine;*/
float float_sin(float f) { return sin(f); }
/*META @meta: label=Cosine;*/
float float_cos(float f) { return cos(f); }
/*META @meta: label=Tangent;*/
float float_tan(float f) { return tan(f); }
/*META @meta: label=Arcsine;*/
float float_asin(float f) { return asin(f); }
/*META @meta: label=Arcosine;*/
float float_acos(float f) { return acos(f); }
/*META @meta: label=Arctangent;*/
float float_atan(float f) { return atan(f); }

/*META @meta: label=Radians to Degrees;*/
float float_degrees(float r) { return degrees(r); }
/*META @meta: label=Degrees to Radians;*/
float float_radians(float d) { return radians(d); }

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

/*META @meta: label=If Else;*/
float float_if_else(bool condition, float if_true, float if_false){ return condition ? if_true : if_false; }

/*META @meta: subcategory=Map Range; label=Float; 
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

#endif //FLOAT_GLSL
