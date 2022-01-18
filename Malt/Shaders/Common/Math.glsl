#ifndef COMMON_MATH_GLSL
#define COMMON_MATH_GLSL

//C Standard constants

#define M_E         2.71828182845904523536028747135266250   /* e */
#define M_LOG2E     1.44269504088896340735992468100189214   /* log2(e) */
#define M_LOG10E    0.434294481903251827651128918916605082  /* log10(e) */
#define M_LN2       0.693147180559945309417232121458176568  /* ln(2) */
#define M_LN10      2.30258509299404568401799145468436421   /* ln(10) */
#define M_PI        3.14159265358979323846264338327950288   /* pi */
#define M_PI_2      1.57079632679489661923132169163975144   /* pi/2 */
#define M_PI_4      0.785398163397448309615660845819875721  /* pi/4 */
#define M_1_PI      0.318309886183790671537767526745028724  /* 1/pi */
#define M_2_PI      0.636619772367581343075535053490057448  /* 2/pi */
#define M_2_SQRTPI  1.12837916709551257389615890312154517   /* 2/sqrt(pi) */
#define M_SQRT2     1.41421356237309504880168872420969808   /* sqrt(2) */
#define M_SQRT1_2   0.707106781186547524400844362104849039  /* 1/sqrt(2) */

#define PI M_PI

//These are defined as macros to make them work across different types. (Poor Man's Generics)

#define saturate(value) clamp((value), 0, 1)

#define map_range(value, from_min, from_max, to_min, to_max) (mix((to_min), (to_max), ((value) - (from_min)) / ((from_max) - (from_min))))
#define map_range_clamped(value, from_min, from_max, to_min, to_max) clamp(map_range(value, from_min, from_max, to_min, to_max), to_min, to_max)

#define snap(value, range) (round((value) / (range)) * (range))

#include "Hash.glsl"

vec4 random_per_sample(float seed)
{
    return hash(vec2(float(SAMPLE_COUNT), seed));
}

vec2 screen_uv(); //FORWARD DECLARATION

vec4 random_per_pixel(float seed) 
{
    return vec4(screen_uv(), float(SAMPLE_COUNT), seed);
}

#endif // COMMON_MATH_GLSL
