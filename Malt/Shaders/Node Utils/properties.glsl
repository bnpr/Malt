#ifndef PROPERTIES_GLSL
#define PROPERTIES_GLSL

/*  META GLOBAL
    @meta: internal = true;
*/

bool bool_property(bool b) { return b; }

float float_property(float f) { return f; }

int int_property(int i) { return i; }

vec2 vec2_property(vec2 v) { return v; }

/*  META @v: subtype=Vector;*/
vec3 vec3_property(vec3 v) { return v; }
/*  META @v: subtype=Vector;*/
vec4 vec4_property(vec4 v) { return v; }

vec3 vec3_color_property(vec3 v) { return v; }
vec4 vec4_color_property(vec4 v) { return v; }

#endif //PROPERTIES_GLSL
