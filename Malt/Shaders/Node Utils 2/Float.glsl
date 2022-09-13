#ifndef NODE_UTILS_2_FLOAT_GLSL
#define NODE_UTILS_2_FLOAT_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Float;
*/

/*META @meta: label=Add;*/
float Float_add(float a, float b){ return a+b; }
/*META @meta: label=Subtract;*/
float Float_subtract(float a, float b){ return a-b; }
/*META @meta: label=Multiply;*/
float Float_multiply(float a, float b){ return a*b; }
/*META @meta: label=Divide;*/
float Float_divide(float a, float b){ return a/b; }
/*META 
    @meta: label=Map Range; 
    @clamped: default=true;
    @value: default = 0.5;
    @from_min: default = 0.0;
    @from_max: default = 1.0;
    @to_min: default = 0.0;
    @to_max: default = 1.0;
*/
float Float_map_range(bool clamped, float value, float from_min, float from_max, float to_min, float to_max)
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
float Float_modulo(float a, float b){ return mod(a,b); }
/*META @meta: label=Power;*/
float Float_pow(float a, float b){ return pow(a, b); }
/*META @meta: label=Square Root;*/
float Float_sqrt(float a){ return sqrt(a); }

/*META @meta: label=Round;*/
float Float_round(float a){ return round(a); }
/*META @meta: label=Fractional Part;*/
float Float_fract(float a){ return fract(a); }
/*META @meta: label=Floor;*/
float Float_floor(float a){ return floor(a); }
/*META @meta: label=Ceil;*/
float Float_ceil(float a){ return ceil(a); }

/*META @meta: label=Clamp; @b: label=Min; @c: label=Max; */
float Float_clamp(float a, float b, float c){ return clamp(a, b, c); }

/*META @meta: label=Sign;*/
float Float_sign(float a){ return sign(a); }
/*META @meta: label=Absolute;*/
float Float_abs(float a){ return abs(a); }
/*META @meta: label=Minimum;*/
float Float_min(float a, float b){ return min(a,b); }
/*META @meta: label=Maximum;*/
float Float_max(float a, float b){ return max(a,b); }

/*META @meta: label=Mix;*/
float Float_mix(float a, float b, float fac){ return mix(a,b,fac); }

/*META @meta: label=Sine;*/
float Float_sin(float a) { return sin(a); }
/*META @meta: label=Cosine;*/
float Float_cos(float a) { return cos(a); }
/*META @meta: label=Tangent;*/
float Float_tan(float a) { return tan(a); }
/*META @meta: label=Arcsine;*/
float Float_asin(float a) { return asin(a); }
/*META @meta: label=Arcosine;*/
float Float_acos(float a) { return acos(a); }
/*META @meta: label=Arctangent;*/
float Float_atan(float a) { return atan(a); }

/*META @meta: label=Radians to Degrees;*/
float Float_degrees(float a) { return degrees(a); }
/*META @meta: label=Degrees to Radians;*/
float Float_radians(float a) { return radians(a); }

/*META @meta: label=Equal; @e: default=0.1; min=0.0; */
bool Float_equal(float a, float b, float e){ return abs(a - b) < abs(e); }
/*META @meta: label=Not Equal; @e: default=0.1; min=0.0; */
bool Float_not_equal(float a, float b, float e){ return !Float_equal(a, b, e); }
/*META @meta: label=Greater;*/
bool Float_greater(float a, float b){ return a > b; }
/*META @meta: label=Greater or Equal;*/
bool Float_greater_or_equal(float a, float b){ return a >= b; }
/*META @meta: label=Less;*/
bool Float_less(float a, float b){ return a < b; }
/*META @meta: label=Less or Equal;*/
bool Float_less_or_equal(float a, float b){ return a <= b; }

/*META @meta: label=If Else; @a: label=If True; @b: label=If False; */
float Float_if_else(bool condition, float a, float b){ return condition ? a : b; }

/* META @meta: label=Ease; @a: min=0.0; max=1.0; subtype=Slider; @b: default=0.55; min=0.0; */
float Float_ease(float a, float b){ return ease(a,b);}

#endif //NODE_UTILS_2_FLOAT_GLSL
