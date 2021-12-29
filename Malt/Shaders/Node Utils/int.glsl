#ifndef INT_GLSL
#define INT_GLSL

int int_property(int i) { return i; }

int int_add(int a, int b){ return a+b; }
int int_subtract(int a, int b){ return a-b; }
int int_multiply(int a, int b){ return a*b; }
int int_divide(int a, int b){ return a/b; }
int int_modulo(int a, int b){ return a%b; }

int int_clamp(int i, int min, int max){ return clamp(i, min, max); }

int int_sign(int i){ return sign(i); }
int int_abs(int i){ return abs(i); }
int int_min(int a, int b){ return min(a,b); }
int int_max(int a, int b){ return max(a,b); }

bool int_equal(int a, int b){ return a == b; }
bool int_not_equal(int a, int b){ return a != b; }
bool int_greater(int a, int b){ return a > b; }
bool int_greater_or_equal(int a, int b){ return a >= b; }
bool int_less(int a, int b){ return a < b; }
bool int_less_or_equal(int a, int b){ return a <= b; }

int int_if_else(bool condition, int a, int b){ return condition ? a : b; }

int int_from_float(float f) { return int(f); }
int int_from_uint(uint u) { return int(u); }

uint uint_from_float(float f) { return uint(f); }
uint uint_from_int(int i) { return uint(i); }

ivec2 ivec2_join(int x, int y){ return ivec2(x,y); }
void ivec2_split(ivec2 v, out int x, out int y){ x = v.x; y = v.y; }

ivec3 ivec3_join(int x, int y, int z){ return ivec3(x,y,z); }
void ivec3_split(ivec3 v, out int x, out int y, out int z){ x = v.x; y = v.y; z = v.z; }

ivec4 ivec4_join(int x, int y, int z, int w){ return ivec4(x,y,z,w); }
void ivec4_split(ivec4 v, out int x, out int y, out int z, out int w){ x = v.x; y = v.y; z = v.z; w = v.w; }

uvec2 uvec2_join(uint x, uint y){ return uvec2(x,y); }
void uvec2_split(uvec2 v, out uint x, out uint y){ x = v.x; y = v.y; }

uvec3 uvec3_join(uint x, uint y, uint z){ return uvec3(x,y,z); }
void uvec3_split(uvec3 v, out uint x, out uint y, out uint z){ x = v.x; y = v.y; z = v.z; }

uvec4 uvec4_join(uint x, uint y, uint z, uint w){ return uvec4(x,y,z,w); }
void uvec4_split(uvec4 v, out uint x, out uint y, out uint z, out uint w){ x = v.x; y = v.y; z = v.z; w = v.w; }

#endif //INT_GLSL
