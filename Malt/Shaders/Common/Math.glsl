#ifndef COMMON_MATH_GLSL
#define COMMON_MATH_GLSL

/*  META GLOBAL
    @meta: category=Math; internal=true;
*/

//C Standard constants

#define M_E             2.71828182845904523536028747135266250   /* e */
#define M_LOG2E         1.44269504088896340735992468100189214   /* log2(e) */
#define M_LOG10E        0.434294481903251827651128918916605082  /* log10(e) */
#define M_LN2           0.693147180559945309417232121458176568  /* ln(2) */
#define M_LN10          2.30258509299404568401799145468436421   /* ln(10) */
#define M_PI            3.14159265358979323846264338327950288   /* pi */
#define M_PI_2          1.57079632679489661923132169163975144   /* pi/2 */
#define M_PI_4          0.785398163397448309615660845819875721  /* pi/4 */
#define M_1_PI          0.318309886183790671537767526745028724  /* 1/pi */
#define M_2_PI          0.636619772367581343075535053490057448  /* 2/pi */
#define M_2_SQRTPI      1.12837916709551257389615890312154517   /* 2/sqrt(pi) */
#define M_SQRT2         1.41421356237309504880168872420969808   /* sqrt(2) */
#define M_SQRT1_2       0.707106781186547524400844362104849039  /* 1/sqrt(2) */

#define GOLDEN_RATIO    1.618033988749894848204586834365638117  /* phi */
#define GOLDEN_ANGLE    2.399963229728652887367000547681316645  /* pi*(3-sqrt(5)) */
#define PI M_PI

//These are defined as macros to make them work across different types. (Poor Man's Generics)

#define saturate(value) clamp((value), 0, 1)

float safe_mix(float a, float b, float f) {return f == 0.0 ? a : f == 1.0 ? b : mix(a, b, f);}
vec2 safe_mix(vec2 a, vec2 b, vec2 f) {return f == vec2(0) ? a : f == vec2(1) ? b : mix(a, b, f);}
vec2 safe_mix(vec2 a, vec2 b, float f) {return f == 0.0 ? a : f == 1.0 ? b : mix(a, b, f);}
vec3 safe_mix(vec3 a, vec3 b, vec3 f) {return f == vec3(0) ? a : f == vec3(1) ? b : mix(a, b, f);}
vec3 safe_mix(vec3 a, vec3 b, float f) {return f == 0.0 ? a : f == 1.0 ? b : mix(a, b, f);}
vec4 safe_mix(vec4 a, vec4 b, vec4 f) {return f == vec4(0) ? a : f == vec4(1) ? b : mix(a, b, f);}
vec4 safe_mix(vec4 a, vec4 b, float f) {return f == 0.0 ? a : f == 1.0 ? b : mix(a, b, f);}

#define map_range(value, from_min, from_max, to_min, to_max) (safe_mix((to_min), (to_max), ((value) - (from_min)) / ((from_max) - (from_min))))
#define map_range_clamped(value, from_min, from_max, to_min, to_max) clamp(map_range(value, from_min, from_max, to_min, to_max), min(to_min, to_max), max(to_max, to_min))

#define snap(value, range) (round((value) / (range)) * (range))
#define distort(base, distortion, fac) (base + (distortion - 0.5) * 2 * fac)

#define vector_angle(a,b) (acos((dot(a,b))/(length(a) * length(b))))

#include "Common.glsl"

float pingpong(float a, float b)
{
    return (b != 0.0)? abs(fract((a - b) / (b * 2.0)) * b * 2.0 - b) : 0.0;
}

/* META @meta: subcategory=Random; */
vec4 random_per_object(float seed)
{
    return hash(vec2(IO_ID.x, seed));
}

/* META @meta: subcategory=Random; */
vec4 random_per_sample(float seed)
{
    return hash(vec2(float(SAMPLE_COUNT), seed));
}

vec2 screen_uv(); //FORWARD DECLARATION

/* META @meta: subcategory=Random; */
vec4 random_per_pixel(float seed) 
{
    return hash(vec4(screen_uv(), float(SAMPLE_COUNT), seed));
}

vec2 phyllotaxis_disk(float p, int total)
{
    // https://en.wikipedia.org/wiki/Phyllotaxis
    // https://www.mathrecreation.com/2008/09/phyllotaxis-spirals.html

    // returns a point on a disk where all points are evenly spaced. The 'total' argument makes sure that your point ends up in a disk of radius=1
    // this is a good approach of getting a spherical kernel with arbitrary sample count
    float r = p * GOLDEN_ANGLE;
    return vec2(cos(r), sin(r)) * vec2(pow(p / float(total), 0.5));
}

#endif // COMMON_MATH_GLSL
