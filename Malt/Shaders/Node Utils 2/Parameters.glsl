#ifndef NODE_UTILS_2_PARAMETERS_GLSL
#define NODE_UTILS_2_PARAMETERS_GLSL

/*META GLOBAL
    @meta: category=Parameters;
*/

/*  META
    @meta: label=Boolean;
*/
bool Bool_property(bool b) { return b; }
/*  META
    @meta: label=Float;
*/
float Float_property(float f) { return f; }
/*  META
    @meta: label=Integer;
*/
int Int_property(int i) { return i; }
/*  META
    @meta: label=Vector 2D;
*/
vec2 Vec2_property(vec2 v) { return v; }

/*  META
    @meta: label=Vector 3D;
    @v: subtype=Vector;
*/
vec3 Vec3_property(vec3 v) { return v; }
/*  META
    @meta: label=Vector 4D;
    @v: subtype=Vector;
*/
vec4 Vec4_property(vec4 v) { return v; }

/*  META
    @meta: label=RGB Color;
    @v: subtype=Color;
*/
vec3 Vec3_color_property(vec3 v) { return v; }
/*  META
    @meta: label=RGBA Color;
    @v: subtype=Color;
*/
vec4 Vec4_color_property(vec4 v) { return v; }

#ifdef RETURN_SAMPLER_SUPPORT
/*  META
    @meta: label=Color Ramp;
*/
sampler1D Sampler1D_property(sampler1D color_ramp) { return color_ramp; }
/*  META
    @meta: label=Image;
*/
sampler2D Sampler2D_property(sampler2D image) { return image; }
#endif

#endif //NODE_UTILS_2_PARAMETERS_GLSL
