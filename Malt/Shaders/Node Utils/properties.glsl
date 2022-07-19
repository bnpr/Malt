#ifndef PROPERTIES_GLSL
#define PROPERTIES_GLSL

/*META GLOBAL
    @meta: category=Parameters;
*/

/*  META
    @meta: label=Boolean;
*/
bool bool_property(bool b) { return b; }
/*  META
    @meta: label=Float;
*/
float float_property(float f) { return f; }
/*  META
    @meta: label=Integer;
*/
int int_property(int i) { return i; }
/*  META
    @meta: label=Vector 2D;
*/
vec2 vec2_property(vec2 v) { return v; }

/*  META
    @meta: label=Vector 3D;
    @v: subtype=Vector;
*/
vec3 vec3_property(vec3 v) { return v; }
/*  META
    @meta: label=Vector 4D;
    @v: subtype=Vector;
*/
vec4 vec4_property(vec4 v) { return v; }

/*  META
    @meta: label=RGB Color;
    @v: subtype=Vector;
*/
vec3 vec3_color_property(vec3 v) { return v; }
/*  META
    @meta: label=RGBA Color;
    @v: subtype=Vector;
*/
vec4 vec4_color_property(vec4 v) { return v; }

/*  META
    @meta: label=Color Ramp;
*/
sampler1D sampler1D_property(sampler1D color_ramp) { return color_ramp; }
/*  META
    @meta: label=Image;
*/
sampler2D sampler2D_property(sampler2D image) { return image; }

#endif //PROPERTIES_GLSL
