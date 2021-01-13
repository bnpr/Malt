
//This file contains a series of C++ macros, structs and function declarations
//to make GLSL autocompletion work with C++ autocompletion implementations

#ifdef __INTELLISENSE__

//Define GLSL keywords

#define in
#define out
#define inout
#define uniform
#define varying
#define layout(index)
#define discard
#define uint unsigned int
#define atomic_uint uint


//Declare GLSL built-in types

struct vec2 {};
struct vec3 {};
struct vec4 {};
struct dvec2 {};
struct dvec3 {};
struct dvec4 {};
struct ivec2 {};
struct ivec3 {};
struct ivec4 {};
struct uvec2 {};
struct uvec3 {};
struct uvec4 {};
struct bvec2 {};
struct bvec3 {};
struct bvec4 {};
struct mat2 {};
struct dmat2 {};
struct mat3 {};
struct dmat3 {};
struct mat4 {};
struct dmat4 {};
struct mat2x2 {};
struct dmat2x2 {};
struct mat2x3 {};
struct dmat2x3 {};
struct mat2x4 {};
struct dmat2x4 {};
struct mat3x2 {};
struct dmat3x2 {};
struct mat3x3 {};
struct dmat3x3 {};
struct mat3x4 {};
struct dmat3x4 {};
struct mat4x2 {};
struct dmat4x2 {};
struct mat4x3 {};
struct dmat4x3 {};
struct mat4x4 {};
struct dmat4x4 {};
struct sampler1D {};
struct isampler1D {};
struct usampler1D {};
struct sampler2D {};
struct isampler2D {};
struct usampler2D {};
struct sampler3D {};
struct isampler3D {};
struct usampler3D {};
struct sampler2DRect {};
struct isampler2DRect {};
struct usampler2DRect {};
struct sampler1DArray {};
struct isampler1DArray {};
struct usampler1DArray {};
struct sampler2DArray {};
struct isampler2DArray {};
struct usampler2DArray {};
struct samplerBuffer {};
struct isamplerBuffer {};
struct usamplerBuffer {};
struct sampler2DMS {};
struct isampler2DMS {};
struct usampler2DMS {};
struct sampler2DMSArray {};
struct isampler2DMSArray {};
struct usampler2DMSArray {};
struct samplerCube {};
struct isamplerCube {};
struct usamplerCube {};
struct samplerCubeArray {};
struct isamplerCubeArray {};
struct usamplerCubeArray {};
struct sampler2DDArray {};
struct isampler2DDArray {};
struct usampler2DDArray {};
struct samplerRect {};
struct isamplerRect {};
struct usamplerRect {};


//Declare GLSL standard library functions

//return the absolute value of the parameter
template<typename T> T abs(T x);
//return the absolute value of the parameter
template<typename I> I abs(I x);
//return the absolute value of the parameter
template<typename D> D abs(D x);
//return the arccosine of the parameter
template<typename T> T acos(T x);
//return the arc hyperbolic cosine of the parameter
template<typename T> T acosh(T x);
//check whether all elements of a boolean vector are true
template<typename bvec> bool all(bvec x);
//check whether any element of a boolean vector is true
template<typename bvec> bool any(bvec x);
//return the arcsine of the parameter
template<typename T> T asin(T x);
//return the arc hyperbolic sine of the parameter
template<typename T> T asinh(T x);
//return the arc-tangent of the parameters
template<typename T> T atan(T y, T x);
//return the arc-tangent of the parameters
template<typename T> T atan(T y_over_x);
//return the arc hyperbolic tangent of the parameter
template<typename T> T atanh(T x);
//counts the number of 1 bits in an integer
template<typename I> I bitCount(I value);
//counts the number of 1 bits in an integer
template<typename I, typename U> I bitCount(U value);
//extract a range of bits from an integer
template<typename I> I bitfieldExtract(I value, int offset, int bits);
//extract a range of bits from an integer
template<typename U> U bitfieldExtract(U value, int offset, int bits);
//insert a range of bits into an integer
template<typename I> I bitfieldInsert(I base, I insert, int offset, int bits);
//insert a range of bits into an integer
template<typename U> U bitfieldInsert(U base, U insert, int offset, int bits);
//reverse the order of bits in an integer
template<typename I> I bitfieldReverse(I value);
//reverse the order of bits in an integer
template<typename U> U bitfieldReverse(U value);
//find the nearest integer that is greater than or equal to the parameter
template<typename T> T ceil(T x);
//find the nearest integer that is greater than or equal to the parameter
template<typename D> D ceil(D x);
//constrain a value to lie between two further values
template<typename T> T clamp(T x, T minVal, T maxVal);
//constrain a value to lie between two further values
template<typename T> T clamp(T x, float minVal, float maxVal);
//constrain a value to lie between two further values
template<typename D> D clamp(D x, D minVal, D maxVal);
//constrain a value to lie between two further values
template<typename D> D clamp(D x, double minVal, double maxVal);
//constrain a value to lie between two further values
template<typename I> I clamp(I x, I minVal, I maxVal);
//constrain a value to lie between two further values
template<typename I> I clamp(I x, int minVal, int maxVal);
//constrain a value to lie between two further values
template<typename U> U clamp(U x, U minVal, U maxVal);
//constrain a value to lie between two further values
template<typename U> U clamp(U x, uint minVal, uint maxVal);
//return the cosine of the parameter
template<typename T> T cos(T angle);
//return the hyperbolic cosine of the parameter
template<typename T> T cosh(T x);
//calculate the cross product of two vectors
vec3 cross(vec3 x, vec3 y);
//calculate the cross product of two vectors
dvec3 cross(dvec3 x, dvec3 y);
//convert a quantity in radians to degrees
template<typename T> T degrees(T radians);
//calculate the determinant of a matrix
float determinant(mat2 m);
//calculate the determinant of a matrix
float determinant(mat3 m);
//calculate the determinant of a matrix
float determinant(mat4 m);
//calculate the determinant of a matrix
double determinant(dmat2 m);
//calculate the determinant of a matrix
double determinant(dmat3 m);
//calculate the determinant of a matrix
double determinant(dmat4 m);
//return the partial derivative of an argument with respect to x or y
template<typename T> T dFdx(T p);
//return the partial derivative of an argument with respect to x or y
template<typename T> T dFdy(T p);
//return the partial derivative of an argument with respect to x or y
template<typename T> T dFdxCoarse(T p);
//return the partial derivative of an argument with respect to x or y
template<typename T> T dFdyCoarse(T p);
//return the partial derivative of an argument with respect to x or y
template<typename T> T dFdxFine(T p);
//return the partial derivative of an argument with respect to x or y
template<typename T> T dFdyFine(T p);
//calculate the distance between two points
template<typename T> float distance(T p0, T p1);
//calculate the distance between two points
template<typename D> double distance(D p0, D p1);
//calculate the dot product of two vectors
template<typename T> float dot(T x, T y);
//calculate the dot product of two vectors
template<typename D> double dot(D x, D y);
//emit a vertex to a specified stream
void EmitStreamVertex(int stream);
//emit a vertex to the first vertex stream
void EmitVertex();
//complete the current output primitive on the first vertex stream
void EndPrimitive();
//complete the current output primitive on a specified stream
void EndStreamPrimitive(int stream);
//perform a component-wise equal-to comparison of two vectors
template<typename bvec, typename vec> bvec equal(vec x, vec y);
//perform a component-wise equal-to comparison of two vectors
template<typename bvec, typename ivec> bvec equal(ivec x, ivec y);
//perform a component-wise equal-to comparison of two vectors
template<typename bvec, typename uvec> bvec equal(uvec x, uvec y);
//return the natural exponentiation of the parameter
template<typename T> T exp(T x);
//return 2 raised to the power of the parameter
template<typename T> T exp2(T x);
//return a vector pointing in the same direction as another
template<typename T> T faceforward(T N, T I, T Nref);
//return a vector pointing in the same direction as another
template<typename D> D faceforward(D N, D I, D Nref);
//find the index of the least significant bit set to 1 in an integer
template<typename I> I findLSB(I value);
//find the index of the least significant bit set to 1 in an integer
template<typename I, typename U> I findLSB(U value);
//find the index of the most significant bit set to 1 in an integer
template<typename I> I findMSB(I value);
//find the index of the most significant bit set to 1 in an integer
template<typename I, typename U> I findMSB(U value);
//produce the encoding of a floating point value as an integer
template<typename I, typename T> I floatBitsToInt(T x);
//produce the encoding of a floating point value as an integer
template<typename U, typename T> U floatBitsToUint(T x);
//find the nearest integer less than or equal to the parameter
template<typename T> T floor(T x);
//find the nearest integer less than or equal to the parameter
template<typename D> D floor(D x);
//perform a fused multiply-add operation
template<typename T> T fma(T a, T b, T c);
//perform a fused multiply-add operation
template<typename D> D fma(D a, D b, D c);
//compute the fractional part of the argument
template<typename T> T fract(T x);
//compute the fractional part of the argument
template<typename D> D fract(D x);
//split a floating point number
template<typename T, typename I> T frexp(T x, out I exp);
//split a floating point number
template<typename D, typename I> D frexp(D x, out I exp);
//return the sum of the absolute value of derivatives in x and y
template<typename T> T fwidth(T p);
//return the sum of the absolute value of derivatives in x and y
template<typename T> T fwidthCoarse(T p);
//return the sum of the absolute value of derivatives in x and y
template<typename T> T fwidthFine(T p);
//perform a component-wise greater-than comparison of two vectors
template<typename bvec, typename vec> bvec greaterThan(vec x, vec y);
//perform a component-wise greater-than comparison of two vectors
template<typename bvec, typename ivec> bvec greaterThan(ivec x, ivec y);
//perform a component-wise greater-than comparison of two vectors
template<typename bvec, typename uvec> bvec greaterThan(uvec x, uvec y);
//perform a component-wise greater-than-or-equal comparison of two vectors
template<typename bvec, typename vec> bvec greaterThanEqual(vec x, vec y);
//perform a component-wise greater-than-or-equal comparison of two vectors
template<typename bvec, typename ivec> bvec greaterThanEqual(ivec x, ivec y);
//perform a component-wise greater-than-or-equal comparison of two vectors
template<typename bvec, typename uvec> bvec greaterThanEqual(uvec x, uvec y);
//produce a floating point using an encoding supplied as an integer
template<typename T, typename I> T intBitsToFloat(I x);
//produce a floating point using an encoding supplied as an integer
template<typename T, typename U> T uintBitsToFloat(U x);
//sample a varying at the centroid of a pixel
float interpolateAtCentroid(float interpolant);
//sample a varying at the centroid of a pixel
vec2 interpolateAtCentroid(vec2 interpolant);
//sample a varying at the centroid of a pixel
vec3 interpolateAtCentroid(vec3 interpolant);
//sample a varying at the centroid of a pixel
vec4 interpolateAtCentroid(vec4 interpolant);
//sample a varying at specified offset from the center of a pixel
float interpolateAtOffset(float interpolant, vec2 offset);
//sample a varying at specified offset from the center of a pixel
vec2 interpolateAtOffset(vec2 interpolant, vec2 offset);
//sample a varying at specified offset from the center of a pixel
vec3 interpolateAtOffset(vec3 interpolant, vec2 offset);
//sample a varying at specified offset from the center of a pixel
vec4 interpolateAtOffset(vec4 interpolant, vec2 offset);
//sample a varying at the location of a specified sample
float interpolateAtSample(float interpolant, int sample);
//sample a varying at the location of a specified sample
vec2 interpolateAtSample(vec2 interpolant, int sample);
//sample a varying at the location of a specified sample
vec3 interpolateAtSample(vec3 interpolant, int sample);
//sample a varying at the location of a specified sample
vec4 interpolateAtSample(vec4 interpolant, int sample);
//calculate the inverse of a matrix
mat2 inverse(mat2 m);
//calculate the inverse of a matrix
mat3 inverse(mat3 m);
//calculate the inverse of a matrix
mat4 inverse(mat4 m);
//calculate the inverse of a matrix
dmat2 inverse(dmat2 m);
//calculate the inverse of a matrix
dmat3 inverse(dmat3 m);
//calculate the inverse of a matrix
dmat4 inverse(dmat4 m);
//return the inverse of the square root of the parameter
template<typename T> T inversesqrt(T x);
//return the inverse of the square root of the parameter
template<typename D> D inversesqrt(D x);
//determine whether the parameter is positive or negative infinity
template<typename B, typename T> B isinf(T x);
//determine whether the parameter is positive or negative infinity
template<typename B, typename D> B isinf(D x);
//determine whether the parameter is a number
template<typename B, typename T> B isnan(T x);
//determine whether the parameter is a number
template<typename B, typename D> B isnan(D x);
//assemble a floating point number from a value and exponent
template<typename T, typename I> T ldexp(T x, I exp);
//assemble a floating point number from a value and exponent
template<typename D, typename I> D ldexp(D x, I exp);
//calculate the length of a vector
template<typename T> float length(T x);
//calculate the length of a vector
template<typename D> double length(D x);
//perform a component-wise less-than comparison of two vectors
template<typename bvec, typename vec> bvec lessThan(vec x, vec y);
//perform a component-wise less-than comparison of two vectors
template<typename bvec, typename ivec> bvec lessThan(ivec x, ivec y);
//perform a component-wise less-than comparison of two vectors
template<typename bvec, typename uvec> bvec lessThan(uvec x, uvec y);
//perform a component-wise less-than-or-equal comparison of two vectors
template<typename bvec, typename vec> bvec lessThanEqual(vec x, vec y);
//perform a component-wise less-than-or-equal comparison of two vectors
template<typename bvec, typename ivec> bvec lessThanEqual(ivec x, ivec y);
//perform a component-wise less-than-or-equal comparison of two vectors
template<typename bvec, typename uvec> bvec lessThanEqual(uvec x, uvec y);
//return the natural logarithm of the parameter
template<typename T> T log(T x);
//return the base 2 logarithm of the parameter
template<typename T> T log2(T x);
//perform a component-wise multiplication of two matrices
template<typename mat> mat matrixCompMult(mat x, mat y);
//perform a component-wise multiplication of two matrices
template<typename dmat> dmat matrixCompMult(dmat x, dmat y);
//return the greater of two values
template<typename T> T max(T x, T y);
//return the greater of two values
template<typename T> T max(T x, float y);
//return the greater of two values
template<typename D> D max(D x, D y);
//return the greater of two values
template<typename D> D max(D x, double y);
//return the greater of two values
template<typename I> I max(I x, I y);
//return the greater of two values
template<typename I> I max(I x, int y);
//return the greater of two values
template<typename U> U max(U x, U y);
//return the greater of two values
template<typename U> U max(U x, uint y);
//return the lesser of two values
template<typename T> T min(T x, T y);
//return the lesser of two values
template<typename T> T min(T x, float y);
//return the lesser of two values
template<typename D> D min(D x, D y);
//return the lesser of two values
template<typename D> D min(D x, double y);
//return the lesser of two values
template<typename I> I min(I x, I y);
//return the lesser of two values
template<typename I> I min(I x, int y);
//return the lesser of two values
template<typename U> U min(U x, U y);
//return the lesser of two values
template<typename U> U min(U x, uint y);
//linearly interpolate between two values
template<typename T> T mix(T x, T y, T a);
//linearly interpolate between two values
template<typename T> T mix(T x, T y, float a);
//linearly interpolate between two values
template<typename D> D mix(D x, D y, D a);
//linearly interpolate between two values
template<typename D> D mix(D x, D y, double a);
//linearly interpolate between two values
template<typename T, typename B> T mix(T x, T y, B a);
//linearly interpolate between two values
template<typename D, typename B> D mix(D x, D y, B a);
//linearly interpolate between two values
template<typename I, typename B> I mix(I x, I y, B a);
//linearly interpolate between two values
template<typename U, typename B> U mix(U x, U y, B a);
//linearly interpolate between two values
template<typename B> B mix(B x, B y, B a);
//compute value of one parameter modulo another
template<typename T> T mod(T x, float y);
//compute value of one parameter modulo another
template<typename T> T mod(T x, T y);
//compute value of one parameter modulo another
template<typename D> D mod(D x, double y);
//compute value of one parameter modulo another
template<typename D> D mod(D x, D y);
//separate a value into its integer and fractional components
template<typename T> T modf(T x, out T i);
//separate a value into its integer and fractional components
template<typename D> D modf(D x, out D i);
//calculates the unit vector in the same direction as the original vector
template<typename T> T normalize(T v);
//calculates the unit vector in the same direction as the original vector
template<typename D> D normalize(D v);
//logically invert a boolean vector
template<typename bvec> bvec not(bvec x);
//perform a component-wise not-equal-to comparison of two vectors
template<typename bvec, typename vec> bvec notEqual(vec x, vec y);
//perform a component-wise not-equal-to comparison of two vectors
template<typename bvec, typename ivec> bvec notEqual(ivec x, ivec y);
//perform a component-wise not-equal-to comparison of two vectors
template<typename bvec, typename uvec> bvec notEqual(uvec x, uvec y);
//calculate the outer product of a pair of vectors
mat2 outerProduct(vec2 c, vec2 r);
//calculate the outer product of a pair of vectors
mat3 outerProduct(vec3 c, vec3 r);
//calculate the outer product of a pair of vectors
mat4 outerProduct(vec4 c, vec4 r);
//calculate the outer product of a pair of vectors
mat2x3 outerProduct(vec3 c, vec2 r);
//calculate the outer product of a pair of vectors
mat3x2 outerProduct(vec2 c, vec3 r);
//calculate the outer product of a pair of vectors
mat2x4 outerProduct(vec4 c, vec2 r);
//calculate the outer product of a pair of vectors
mat4x2 outerProduct(vec2 c, vec4 r);
//calculate the outer product of a pair of vectors
mat3x4 outerProduct(vec4 c, vec3 r);
//calculate the outer product of a pair of vectors
mat4x3 outerProduct(vec3 c, vec4 r);
//calculate the outer product of a pair of vectors
dmat2 outerProduct(dvec2 c, dvec2 r);
//calculate the outer product of a pair of vectors
dmat3 outerProduct(dvec3 c, dvec3 r);
//calculate the outer product of a pair of vectors
dmat4 outerProduct(dvec4 c, dvec4 r);
//calculate the outer product of a pair of vectors
dmat2x3 outerProduct(dvec3 c, dvec2 r);
//calculate the outer product of a pair of vectors
dmat3x2 outerProduct(dvec2 c, dvec3 r);
//calculate the outer product of a pair of vectors
dmat2x4 outerProduct(dvec4 c, dvec2 r);
//calculate the outer product of a pair of vectors
dmat4x2 outerProduct(dvec2 c, dvec4 r);
//calculate the outer product of a pair of vectors
dmat3x4 outerProduct(dvec4 c, dvec3 r);
//calculate the outer product of a pair of vectors
dmat4x3 outerProduct(dvec3 c, dvec4 r);
//create a double-precision value from a pair of unsigned integers
double packDouble2x32(uvec2 v);
//convert two 32-bit floating-point quantities to 16-bit quantities and pack them into a single 32-bit integer
uint packHalf2x16(vec2 v);
//pack floating-point values into an unsigned integer
uint packUnorm2x16(vec2 v);
//pack floating-point values into an unsigned integer
uint packSnorm2x16(vec2 v);
//pack floating-point values into an unsigned integer
uint packUnorm4x8(vec4 v);
//pack floating-point values into an unsigned integer
uint packSnorm4x8(vec4 v);
//return the value of the first parameter raised to the power of the second
template<typename T> T pow(T x, T y);
//convert a quantity in degrees to radians
template<typename T> T radians(T degrees);
//calculate the reflection direction for an incident vector
template<typename T> T reflect(T I, T N);
//calculate the reflection direction for an incident vector
template<typename D> D reflect(D I, D N);
//calculate the refraction direction for an incident vector
template<typename T> T refract(T I, T N, float eta);
//calculate the refraction direction for an incident vector
template<typename D> D refract(D I, D N, float eta);
//find the nearest integer to the parameter
template<typename T> T round(T x);
//find the nearest integer to the parameter
template<typename D> D round(D x);
//find the nearest even integer to the parameter
template<typename T> T roundEven(T x);
//find the nearest even integer to the parameter
template<typename D> D roundEven(D x);
//extract the sign of the parameter
template<typename T> T sign(T x);
//extract the sign of the parameter
template<typename I> I sign(I x);
//extract the sign of the parameter
template<typename D> D sign(D x);
//return the sine of the parameter
template<typename T> T sin(T angle);
//return the hyperbolic sine of the parameter
template<typename T> T sinh(T x);
//perform Hermite interpolation between two values
template<typename T> T smoothstep(T edge0, T edge1, T x);
//perform Hermite interpolation between two values
template<typename T> T smoothstep(float edge0, float edge1, T x);
//perform Hermite interpolation between two values
template<typename D> D smoothstep(D edge0, D edge1, D x);
//perform Hermite interpolation between two values
template<typename D> D smoothstep(double edge0, double edge1, D x);
//return the square root of the parameter
template<typename T> T sqrt(T x);
//return the square root of the parameter
template<typename D> D sqrt(D x);
//generate a step function by comparing two values
template<typename T> T step(T edge, T x);
//generate a step function by comparing two values
template<typename T> T step(float edge, T x);
//generate a step function by comparing two values
template<typename D> D step(D edge, D x);
//generate a step function by comparing two values
template<typename D> D step(double edge, D x);
//return the tangent of the parameter
template<typename T> T tan(T angle);
//return the hyperbolic tangent of the parameter
template<typename T> T tanh(T x);
//perform a lookup of a single texel within a texture
template<typename gvec4, typename gsampler1D> gvec4 texelFetch(gsampler1D sampler, int P, int lod);
//perform a lookup of a single texel within a texture
template<typename gvec4, typename gsampler2D> gvec4 texelFetch(gsampler2D sampler, ivec2 P, int lod);
//perform a lookup of a single texel within a texture
template<typename gvec4, typename gsampler3D> gvec4 texelFetch(gsampler3D sampler, ivec3 P, int lod);
//perform a lookup of a single texel within a texture
template<typename gvec4, typename gsampler2DRect> gvec4 texelFetch(gsampler2DRect sampler, ivec2 P);
//perform a lookup of a single texel within a texture
template<typename gvec4, typename gsampler1DArray> gvec4 texelFetch(gsampler1DArray sampler, ivec2 P, int lod);
//perform a lookup of a single texel within a texture
template<typename gvec4, typename gsampler2DArray> gvec4 texelFetch(gsampler2DArray sampler, ivec3 P, int lod);
//perform a lookup of a single texel within a texture
template<typename gvec4, typename gsamplerBuffer> gvec4 texelFetch(gsamplerBuffer sampler, int P);
//perform a lookup of a single texel within a texture
template<typename gvec4, typename gsampler2DMS> gvec4 texelFetch(gsampler2DMS sampler, ivec2 P, int sample);
//perform a lookup of a single texel within a texture
template<typename gvec4, typename gsampler2DMSArray> gvec4 texelFetch(gsampler2DMSArray sampler, ivec3 P, int sample);
//perform a lookup of a single texel within a texture with an offset
template<typename gvec4, typename gsampler1D> gvec4 texelFetchOffset(gsampler1D sampler, int P, int lod, int offset);
//perform a lookup of a single texel within a texture with an offset
template<typename gvec4, typename gsampler2D> gvec4 texelFetchOffset(gsampler2D sampler, ivec2 P, int lod, ivec2 offset);
//perform a lookup of a single texel within a texture with an offset
template<typename gvec4, typename gsampler3D> gvec4 texelFetchOffset(gsampler3D sampler, ivec3 P, int lod, ivec3 offset);
//perform a lookup of a single texel within a texture with an offset
template<typename gvec4, typename gsampler2DRect> gvec4 texelFetchOffset(gsampler2DRect sampler, ivec2 P, ivec2 offset);
//perform a lookup of a single texel within a texture with an offset
template<typename gvec4, typename gsampler1DArray> gvec4 texelFetchOffset(gsampler1DArray sampler, ivec2 P, int lod, ivec2 offset);
//perform a lookup of a single texel within a texture with an offset
template<typename gvec4, typename gsampler2DArray> gvec4 texelFetchOffset(gsampler2DArray sampler, ivec3 P, int lod, ivec3 offset);
//retrieves texels from a texture
template<typename gvec4, typename gsampler1D> gvec4 texture(gsampler1D sampler, float P);
//retrieves texels from a texture
template<typename gvec4, typename gsampler1D> gvec4 texture(gsampler1D sampler, float P, float  bias);
//retrieves texels from a texture
template<typename gvec4, typename gsampler2D> gvec4 texture(gsampler2D sampler, vec2 P);
//retrieves texels from a texture
template<typename gvec4, typename gsampler2D> gvec4 texture(gsampler2D sampler, vec2 P, float  bias);
//retrieves texels from a texture
template<typename gvec4, typename gsampler3D> gvec4 texture(gsampler3D sampler, vec3 P);
//retrieves texels from a texture
template<typename gvec4, typename gsampler3D> gvec4 texture(gsampler3D sampler, vec3 P, float  bias);
//retrieves texels from a texture
template<typename gvec4, typename gsamplerCube> gvec4 texture(gsamplerCube sampler, vec3 P);
//retrieves texels from a texture
template<typename gvec4, typename gsamplerCube> gvec4 texture(gsamplerCube sampler, vec3 P, float  bias);
//retrieves texels from a texture
template<typename gvec4, typename gsampler1DArray> gvec4 texture(gsampler1DArray sampler, vec2 P);
//retrieves texels from a texture
template<typename gvec4, typename gsampler1DArray> gvec4 texture(gsampler1DArray sampler, vec2 P, float  bias);
//retrieves texels from a texture
template<typename gvec4, typename gsampler2DArray> gvec4 texture(gsampler2DArray sampler, vec3 P);
//retrieves texels from a texture
template<typename gvec4, typename gsampler2DArray> gvec4 texture(gsampler2DArray sampler, vec3 P, float  bias);
//retrieves texels from a texture
template<typename gvec4, typename gsamplerCubeArray> gvec4 texture(gsamplerCubeArray sampler, vec4 P);
//retrieves texels from a texture
template<typename gvec4, typename gsamplerCubeArray> gvec4 texture(gsamplerCubeArray sampler, vec4 P, float  bias);
//retrieves texels from a texture
template<typename gvec4, typename gsampler2DRect> gvec4 texture(gsampler2DRect sampler, vec2 P);
//gathers four texels from a texture
template<typename gvec4, typename gsampler2D> gvec4 textureGather(gsampler2D sampler, vec2 P);
//gathers four texels from a texture
template<typename gvec4, typename gsampler2D> gvec4 textureGather(gsampler2D sampler, vec2 P, int comp);
//gathers four texels from a texture
template<typename gvec4, typename gsampler2DArray> gvec4 textureGather(gsampler2DArray sampler, vec3 P);
//gathers four texels from a texture
template<typename gvec4, typename gsampler2DArray> gvec4 textureGather(gsampler2DArray sampler, vec3 P, int comp);
//gathers four texels from a texture
template<typename gvec4, typename gsamplerCube> gvec4 textureGather(gsamplerCube sampler, vec3 P);
//gathers four texels from a texture
template<typename gvec4, typename gsamplerCube> gvec4 textureGather(gsamplerCube sampler, vec3 P, int comp);
//gathers four texels from a texture
template<typename gvec4, typename gsamplerCubeArray> gvec4 textureGather(gsamplerCubeArray sampler, vec4 P);
//gathers four texels from a texture
template<typename gvec4, typename gsamplerCubeArray> gvec4 textureGather(gsamplerCubeArray sampler, vec4 P, int comp);
//gathers four texels from a texture
template<typename gvec4, typename gsampler2DRect> gvec4 textureGather(gsampler2DRect sampler, vec3 P);
//gathers four texels from a texture
template<typename gvec4, typename gsampler2DRect> gvec4 textureGather(gsampler2DRect sampler, vec3 P, int comp);
//gathers four texels from a texture with offset
template<typename gvec4, typename gsampler2D> gvec4 textureGatherOffset(gsampler2D sampler, vec2 P, ivec2 offset);
//gathers four texels from a texture with offset
template<typename gvec4, typename gsampler2D> gvec4 textureGatherOffset(gsampler2D sampler, vec2 P, ivec2 offset, int comp);
//gathers four texels from a texture with offset
template<typename gvec4, typename gsampler2DArray> gvec4 textureGatherOffset(gsampler2DArray sampler, vec3 P, ivec2 offset);
//gathers four texels from a texture with offset
template<typename gvec4, typename gsampler2DArray> gvec4 textureGatherOffset(gsampler2DArray sampler, vec3 P, ivec2 offset, int comp);
//gathers four texels from a texture with offset
template<typename gvec4, typename gsampler2DRect> gvec4 textureGatherOffset(gsampler2DRect sampler, vec3 P, ivec2 offset);
//gathers four texels from a texture with offset
template<typename gvec4, typename gsampler2DRect> gvec4 textureGatherOffset(gsampler2DRect sampler, vec3 P, ivec2 offset, int comp);
//gathers four texels from a texture with an array of offsets
template<typename gvec4, typename gsampler2D> gvec4 textureGatherOffsets(gsampler2D sampler, vec2 P, ivec2 offsets[4]);
//gathers four texels from a texture with an array of offsets
template<typename gvec4, typename gsampler2D> gvec4 textureGatherOffsets(gsampler2D sampler, vec2 P, ivec2 offsets[4], int comp);
//gathers four texels from a texture with an array of offsets
template<typename gvec4, typename gsampler2DArray> gvec4 textureGatherOffsets(gsampler2DArray sampler, vec3 P, ivec2 offsets[4]);
//gathers four texels from a texture with an array of offsets
template<typename gvec4, typename gsampler2DArray> gvec4 textureGatherOffsets(gsampler2DArray sampler, vec3 P, ivec2 offsets[4], int comp);
//gathers four texels from a texture with an array of offsets
template<typename gvec4, typename gsampler2DRect> gvec4 textureGatherOffsets(gsampler2DRect sampler, vec3 P, ivec2 offsets[4]);
//gathers four texels from a texture with an array of offsets
template<typename gvec4, typename gsampler2DRect> gvec4 textureGatherOffsets(gsampler2DRect sampler, vec3 P, ivec2 offsets[4], int comp);
//perform a texture lookup with explicit gradients
template<typename gvec4, typename gsampler1D> gvec4 textureGrad(gsampler1D sampler, float P, float dPdx, float dPdy);
//perform a texture lookup with explicit gradients
template<typename gvec4, typename gsampler2D> gvec4 textureGrad(gsampler2D sampler, vec2 P, vec2 dPdx, vec2 dPdy);
//perform a texture lookup with explicit gradients
template<typename gvec4, typename gsampler3D> gvec4 textureGrad(gsampler3D sampler, vec3 P, vec3 dPdx, vec3 dPdy);
//perform a texture lookup with explicit gradients
template<typename gvec4, typename gsamplerCube> gvec4 textureGrad(gsamplerCube sampler, vec3 P, vec3 dPdx, vec3 dPdy);
//perform a texture lookup with explicit gradients
template<typename gvec4, typename gsampler2DRect> gvec4 textureGrad(gsampler2DRect sampler, vec2 P, vec2 dPdx, vec2 dPdy);
//perform a texture lookup with explicit gradients
template<typename gvec4, typename gsampler1DArray> gvec4 textureGrad(gsampler1DArray sampler, vec2 P, float dPdx, float dPdy);
//perform a texture lookup with explicit gradients
template<typename gvec4, typename gsampler2DArray> gvec4 textureGrad(gsampler2DArray sampler, vec3 P, vec2 dPdx, vec2 dPdy);
//perform a texture lookup with explicit gradients
template<typename gvec4, typename gsamplerCubeArray> gvec4 textureGrad(gsamplerCubeArray sampler, vec4 P, vec3 dPdx, vec3 dPdy);
//perform a texture lookup with explicit gradients and offset
template<typename gvec4, typename gsampler1D> gvec4 textureGradOffset(gsampler1D sampler, float P, float dPdx, float dPdy, int offset);
//perform a texture lookup with explicit gradients and offset
template<typename gvec4, typename gsampler2D> gvec4 textureGradOffset(gsampler2D sampler, vec2 P, vec2 dPdx, vec2 dPdy, ivec2 offset);
//perform a texture lookup with explicit gradients and offset
template<typename gvec4, typename gsampler3D> gvec4 textureGradOffset(gsampler3D sampler, vec3 P, vec3 dPdx, vec3 dPdy, ivec3 offset);
//perform a texture lookup with explicit gradients and offset
template<typename gvec4, typename gsampler2DRect> gvec4 textureGradOffset(gsampler2DRect sampler, vec2 P, vec2 dPdx, vec2 dPdy, ivec2 offset);
//perform a texture lookup with explicit gradients and offset
template<typename gvec4, typename gsampler1DArray> gvec4 textureGradOffset(gsampler1DArray sampler, vec2 P, float dPdx, float dPdy, int offset);
//perform a texture lookup with explicit gradients and offset
template<typename gvec4, typename gsampler2DArray> gvec4 textureGradOffset(gsampler2DArray sampler, vec3 P, vec2 dPdx, vec2 dPdy, ivec2 offset);
//perform a texture lookup with explicit level-of-detail
template<typename gvec4, typename gsampler1D> gvec4 textureLod(gsampler1D sampler, float P, float lod);
//perform a texture lookup with explicit level-of-detail
template<typename gvec4, typename gsampler2D> gvec4 textureLod(gsampler2D sampler, vec2 P, float lod);
//perform a texture lookup with explicit level-of-detail
template<typename gvec4, typename gsampler3D> gvec4 textureLod(gsampler3D sampler, vec3 P, float lod);
//perform a texture lookup with explicit level-of-detail
template<typename gvec4, typename gsamplerCube> gvec4 textureLod(gsamplerCube sampler, vec3 P, float lod);
//perform a texture lookup with explicit level-of-detail
template<typename gvec4, typename gsampler1DArray> gvec4 textureLod(gsampler1DArray sampler, vec2 P, float lod);
//perform a texture lookup with explicit level-of-detail
template<typename gvec4, typename gsampler2DArray> gvec4 textureLod(gsampler2DArray sampler, vec3 P, float lod);
//perform a texture lookup with explicit level-of-detail
template<typename gvec4, typename gsamplerCubeArray> gvec4 textureLod(gsamplerCubeArray sampler, vec4 P, float lod);
//perform a texture lookup with explicit level-of-detail and offset
template<typename gvec4, typename gsampler1D> gvec4 textureLodOffset(gsampler1D sampler, float P, float lod, int offset);
//perform a texture lookup with explicit level-of-detail and offset
template<typename gvec4, typename gsampler2D> gvec4 textureLodOffset(gsampler2D sampler, vec2 P, float lod, ivec2 offset);
//perform a texture lookup with explicit level-of-detail and offset
template<typename gvec4, typename gsampler3D> gvec4 textureLodOffset(gsampler3D sampler, vec3 P, float lod, ivec3 offset);
//perform a texture lookup with explicit level-of-detail and offset
template<typename gvec4, typename gsampler1DArray> gvec4 textureLodOffset(gsampler1DArray sampler, vec2 P, float lod, int offset);
//perform a texture lookup with explicit level-of-detail and offset
template<typename gvec4, typename gsampler2DArray> gvec4 textureLodOffset(gsampler2DArray sampler, vec3 P, float lod, ivec2 offset);
//perform a texture lookup with offset
template<typename gvec4, typename gsampler1D> gvec4 textureOffset(gsampler1D sampler, float P, int offset);
//perform a texture lookup with offset
template<typename gvec4, typename gsampler1D> gvec4 textureOffset(gsampler1D sampler, float P, int offset, float  bias);
//perform a texture lookup with offset
template<typename gvec4, typename gsampler2D> gvec4 textureOffset(gsampler2D sampler, vec2 P, ivec2 offset);
//perform a texture lookup with offset
template<typename gvec4, typename gsampler2D> gvec4 textureOffset(gsampler2D sampler, vec2 P, ivec2 offset, float  bias);
//perform a texture lookup with offset
template<typename gvec4, typename gsampler3D> gvec4 textureOffset(gsampler3D sampler, vec3 P, ivec3 offset);
//perform a texture lookup with offset
template<typename gvec4, typename gsampler3D> gvec4 textureOffset(gsampler3D sampler, vec3 P, ivec3 offset, float  bias);
//perform a texture lookup with offset
template<typename gvec4, typename gsampler2DRect> gvec4 textureOffset(gsampler2DRect sampler, vec2 P, ivec2 offset);
//perform a texture lookup with offset
template<typename gvec4, typename gsampler1DArray> gvec4 textureOffset(gsampler1DArray sampler, vec2 P, int offset);
//perform a texture lookup with offset
template<typename gvec4, typename gsampler1DArray> gvec4 textureOffset(gsampler1DArray sampler, vec2 P, int offset, float  bias);
//perform a texture lookup with offset
template<typename gvec4, typename gsampler2DArray> gvec4 textureOffset(gsampler2DArray sampler, vec3 P, ivec2 offset);
//perform a texture lookup with offset
template<typename gvec4, typename gsampler2DArray> gvec4 textureOffset(gsampler2DArray sampler, vec3 P, ivec2 offset, float  bias);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler1D> gvec4 textureProj(gsampler1D sampler, vec2 P);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler1D> gvec4 textureProj(gsampler1D sampler, vec2 P, float  bias);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler1D> gvec4 textureProj(gsampler1D sampler, vec4 P);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler1D> gvec4 textureProj(gsampler1D sampler, vec4 P, float  bias);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler2D> gvec4 textureProj(gsampler2D sampler, vec3 P);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler2D> gvec4 textureProj(gsampler2D sampler, vec3 P, float  bias);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler2D> gvec4 textureProj(gsampler2D sampler, vec4 P);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler2D> gvec4 textureProj(gsampler2D sampler, vec4 P, float  bias);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler3D> gvec4 textureProj(gsampler3D sampler, vec4 P);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler3D> gvec4 textureProj(gsampler3D sampler, vec4 P, float  bias);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler2DRect> gvec4 textureProj(gsampler2DRect sampler, vec3 P);
//perform a texture lookup with projection
template<typename gvec4, typename gsampler2DRect> gvec4 textureProj(gsampler2DRect sampler, vec4 P);
//perform a texture lookup with projection and explicit gradients
template<typename gvec4, typename gsampler1D> gvec4 textureProjGrad(gsampler1D sampler, vec2 P, float pDx, float pDy);
//perform a texture lookup with projection and explicit gradients
template<typename gvec4, typename gsampler1D> gvec4 textureProjGrad(gsampler1D sampler, vec4 P, float pDx, float pDy);
//perform a texture lookup with projection and explicit gradients
template<typename gvec4, typename gsampler2D> gvec4 textureProjGrad(gsampler2D sampler, vec3 P, vec2 pDx, vec2 pDy);
//perform a texture lookup with projection and explicit gradients
template<typename gvec4, typename gsampler2D> gvec4 textureProjGrad(gsampler2D sampler, vec4 P, vec2 pDx, vec2 pDy);
//perform a texture lookup with projection and explicit gradients
template<typename gvec4, typename gsampler3D> gvec4 textureProjGrad(gsampler3D sampler, vec4 P, vec3 pDx, vec3 pDy);
//perform a texture lookup with projection and explicit gradients
template<typename gvec4, typename gsampler2DRect> gvec4 textureProjGrad(gsampler2DRect sampler, vec3 P, vec2 pDx, vec2 pDy);
//perform a texture lookup with projection and explicit gradients
template<typename gvec4, typename gsampler2DRect> gvec4 textureProjGrad(gsampler2DRect sampler, vec4 P, vec2 pDx, vec2 pDy);
//perform a texture lookup with projection, explicit gradients and offset
template<typename gvec4, typename gsampler1D> gvec4 textureProjGradOffset(gsampler1D sampler, vec2 P, float dPdx, float dPdy, int offset);
//perform a texture lookup with projection, explicit gradients and offset
template<typename gvec4, typename gsampler1D> gvec4 textureProjGradOffset(gsampler1D sampler, vec4 P, float dPdx, float dPdy, int offset);
//perform a texture lookup with projection, explicit gradients and offset
template<typename gvec4, typename gsampler2D> gvec4 textureProjGradOffset(gsampler2D sampler, vec3 P, vec2 dPdx, vec2 dPdy, ivec2 offset);
//perform a texture lookup with projection, explicit gradients and offset
template<typename gvec4, typename gsampler2D> gvec4 textureProjGradOffset(gsampler2D sampler, vec4 P, vec2 dPdx, vec2 dPdy, ivec2 offset);
//perform a texture lookup with projection, explicit gradients and offset
template<typename gvec4, typename gsampler3D> gvec4 textureProjGradOffset(gsampler3D sampler, vec4 P, vec3 dPdx, vec3 dPdy, ivec3 offset);
//perform a texture lookup with projection, explicit gradients and offset
template<typename gvec4, typename gsampler2DRect> gvec4 textureProjGradOffset(gsampler2DRect sampler, vec3 P, vec2 dPdx, vec2 dPdy, ivec2 offset);
//perform a texture lookup with projection, explicit gradients and offset
template<typename gvec4, typename gsampler2DRect> gvec4 textureProjGradOffset(gsampler2DRect sampler, vec4 P, vec2 dPdx, vec2 dPdy, ivec2 offset);
//perform a texture lookup with projection and explicit level-of-detail
template<typename gvec4, typename gsampler1D> gvec4 textureProjLod(gsampler1D sampler, vec2 P, float lod);
//perform a texture lookup with projection and explicit level-of-detail
template<typename gvec4, typename gsampler1D> gvec4 textureProjLod(gsampler1D sampler, vec4 P, float lod);
//perform a texture lookup with projection and explicit level-of-detail
template<typename gvec4, typename gsampler2D> gvec4 textureProjLod(gsampler2D sampler, vec3 P, float lod);
//perform a texture lookup with projection and explicit level-of-detail
template<typename gvec4, typename gsampler2D> gvec4 textureProjLod(gsampler2D sampler, vec4 P, float lod);
//perform a texture lookup with projection and explicit level-of-detail
template<typename gvec4, typename gsampler3D> gvec4 textureProjLod(gsampler3D sampler, vec4 P, float lod);
//perform a texture lookup with projection and explicit level-of-detail and offset
template<typename gvec4, typename gsampler1D> gvec4 textureProjLodOffset(gsampler1D sampler, vec2 P, float lod, int offset);
//perform a texture lookup with projection and explicit level-of-detail and offset
template<typename gvec4, typename gsampler1D> gvec4 textureProjLodOffset(gsampler1D sampler, vec4 P, float lod, int offset);
//perform a texture lookup with projection and explicit level-of-detail and offset
template<typename gvec4, typename gsampler2D> gvec4 textureProjLodOffset(gsampler2D sampler, vec3 P, float lod, ivec2 offset);
//perform a texture lookup with projection and explicit level-of-detail and offset
template<typename gvec4, typename gsampler2D> gvec4 textureProjLodOffset(gsampler2D sampler, vec4 P, float lod, ivec2 offset);
//perform a texture lookup with projection and explicit level-of-detail and offset
template<typename gvec4, typename gsampler3D> gvec4 textureProjLodOffset(gsampler3D sampler, vec4 P, float lod, ivec3 offset);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler1D> gvec4 textureProjOffset(gsampler1D sampler, vec2 P, int offset);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler1D> gvec4 textureProjOffset(gsampler1D sampler, vec2 P, int offset, float  bias);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler1D> gvec4 textureProjOffset(gsampler1D sampler, vec4 P, int offset);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler1D> gvec4 textureProjOffset(gsampler1D sampler, vec4 P, int offset, float  bias);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler2D> gvec4 textureProjOffset(gsampler2D sampler, vec3 P, ivec2 offset);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler2D> gvec4 textureProjOffset(gsampler2D sampler, vec3 P, ivec2 offset, float  bias);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler2D> gvec4 textureProjOffset(gsampler2D sampler, vec4 P, ivec2 offset);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler2D> gvec4 textureProjOffset(gsampler2D sampler, vec4 P, ivec2 offset, float  bias);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler3D> gvec4 textureProjOffset(gsampler3D sampler, vec4 P, ivec3 offset);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler3D> gvec4 textureProjOffset(gsampler3D sampler, vec4 P, ivec3 offset, float  bias);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler2DRect> gvec4 textureProjOffset(gsampler2DRect sampler, vec3 P, ivec2 offset);
//perform a texture lookup with projection and offset
template<typename gvec4, typename gsampler2DRect> gvec4 textureProjOffset(gsampler2DRect sampler, vec4 P, ivec2 offset);
//compute the number of accessible mipmap levels of a texture
template<typename gsampler1D> int textureQueryLevels(gsampler1D sampler);
//compute the number of accessible mipmap levels of a texture
template<typename gsampler2D> int textureQueryLevels(gsampler2D sampler);
//compute the number of accessible mipmap levels of a texture
template<typename gsampler3D> int textureQueryLevels(gsampler3D sampler);
//compute the number of accessible mipmap levels of a texture
template<typename gsamplerCube> int textureQueryLevels(gsamplerCube sampler);
//compute the number of accessible mipmap levels of a texture
template<typename gsampler1DArray> int textureQueryLevels(gsampler1DArray sampler);
//compute the number of accessible mipmap levels of a texture
template<typename gsampler2DDArray> int textureQueryLevels(gsampler2DDArray sampler);
//compute the number of accessible mipmap levels of a texture
template<typename gsamplerCubeArray> int textureQueryLevels(gsamplerCubeArray sampler);
//compute the level-of-detail that would be used to sample from a texture
template<typename gsampler1D> vec2 textureQueryLod(gsampler1D sampler, float P);
//compute the level-of-detail that would be used to sample from a texture
template<typename gsampler2D> vec2 textureQueryLod(gsampler2D sampler, vec2 P);
//compute the level-of-detail that would be used to sample from a texture
template<typename gsampler3D> vec2 textureQueryLod(gsampler3D sampler, vec3 P);
//compute the level-of-detail that would be used to sample from a texture
template<typename gsamplerCube> vec2 textureQueryLod(gsamplerCube sampler, vec3 P);
//compute the level-of-detail that would be used to sample from a texture
template<typename gsampler1DArray> vec2 textureQueryLod(gsampler1DArray sampler, float P);
//compute the level-of-detail that would be used to sample from a texture
template<typename gsampler2DDArray> vec2 textureQueryLod(gsampler2DDArray sampler, vec2 P);
//compute the level-of-detail that would be used to sample from a texture
template<typename gsamplerCubeArray> vec2 textureQueryLod(gsamplerCubeArray sampler, vec3 P);
//return the number of samples of a texture
template<typename gsampler2DMS> int textureSamples(gsampler2DMS sampler);
//return the number of samples of a texture
template<typename gsampler2DMSArray> int textureSamples(gsampler2DMSArray sampler);
//retrieve the dimensions of a level of a texture
template<typename gsampler1D> int textureSize(gsampler1D sampler, int lod);
//retrieve the dimensions of a level of a texture
template<typename gsampler2D> ivec2 textureSize(gsampler2D sampler, int lod);
//retrieve the dimensions of a level of a texture
template<typename gsampler3D> ivec3 textureSize(gsampler3D sampler, int lod);
//retrieve the dimensions of a level of a texture
template<typename gsamplerCube> ivec2 textureSize(gsamplerCube sampler, int lod);
//retrieve the dimensions of a level of a texture
ivec3 textureSize(samplerCubeArray sampler, int lod);
//retrieve the dimensions of a level of a texture
template<typename gsamplerRect> ivec2 textureSize(gsamplerRect sampler);
//retrieve the dimensions of a level of a texture
template<typename gsampler1DArray> ivec2 textureSize(gsampler1DArray sampler, int lod);
//retrieve the dimensions of a level of a texture
template<typename gsampler2DArray> ivec3 textureSize(gsampler2DArray sampler, int lod);
//retrieve the dimensions of a level of a texture
template<typename gsamplerBuffer> int textureSize(gsamplerBuffer sampler);
//retrieve the dimensions of a level of a texture
template<typename gsampler2DMS> ivec2 textureSize(gsampler2DMS sampler);
//retrieve the dimensions of a level of a texture
template<typename gsampler2DMSArray> ivec3 textureSize(gsampler2DMSArray sampler);
//calculate the transpose of a matrix
mat2 transpose(mat2 m);
//calculate the transpose of a matrix
mat3 transpose(mat3 m);
//calculate the transpose of a matrix
mat4 transpose(mat4 m);
//calculate the transpose of a matrix
mat2x3 transpose(mat3x2 m);
//calculate the transpose of a matrix
mat2x4 transpose(mat4x2 m);
//calculate the transpose of a matrix
mat3x2 transpose(mat2x3 m);
//calculate the transpose of a matrix
mat3x4 transpose(mat4x3 m);
//calculate the transpose of a matrix
mat4x2 transpose(mat2x4 m);
//calculate the transpose of a matrix
mat4x3 transpose(mat3x4 m);
//calculate the transpose of a matrix
dmat2 transpose(dmat2 m);
//calculate the transpose of a matrix
dmat3 transpose(dmat3 m);
//calculate the transpose of a matrix
dmat4 transpose(dmat4 m);
//calculate the transpose of a matrix
dmat2x3 transpose(dmat3x2 m);
//calculate the transpose of a matrix
dmat2x4 transpose(dmat4x2 m);
//calculate the transpose of a matrix
dmat3x2 transpose(dmat2x3 m);
//calculate the transpose of a matrix
dmat3x4 transpose(dmat4x3 m);
//calculate the transpose of a matrix
dmat4x2 transpose(dmat2x4 m);
//calculate the transpose of a matrix
dmat4x3 transpose(dmat3x4 m);
//find the truncated value of the parameter
template<typename T> T trunc(T x);
//find the truncated value of the parameter
template<typename D> D trunc(D x);
//add unsigned integers and generate carry
template<typename U> U uaddCarry(U x, U y, out U carry);
//perform a 32- by 32-bit multiply to produce a 64-bit result
template<typename U> void umulExtended(U x, U y, out U msb, out U lsb);
//perform a 32- by 32-bit multiply to produce a 64-bit result
template<typename I> void imulExtended(I x, I y, out I msb, out I lsb);
//produce two unsigned integers containing the bit encoding of a double precision floating point value
uvec2 unpackDouble2x32(double d);
//convert two 16-bit floating-point values packed into a single 32-bit integer into a vector of two 32-bit floating-point quantities
vec2 unpackHalf2x16(uint v);
//unpack floating-point values from an unsigned integer
vec2 unpackUnorm2x16(uint p);
//unpack floating-point values from an unsigned integer
vec2 unpackSnorm2x16(uint p);
//unpack floating-point values from an unsigned integer
vec4 unpackUnorm4x8(uint p);
//unpack floating-point values from an unsigned integer
vec4 unpackSnorm4x8(uint p);
//subtract unsigned integers and generate borrow
template<typename U> U usubBorrow(U x, U y, out U borrow);


#endif
