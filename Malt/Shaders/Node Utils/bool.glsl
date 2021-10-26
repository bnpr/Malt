#ifndef BOOL_GLSL
#define BOOL_GLSL

bool bool_property(bool b) { return b; }
bool bool_true() { return true; } 
bool bool_false() { return false; }

bool bool_and(bool a, bool b) { return a && b; }
bool bool_or(bool a, bool b) { return a || b; }
bool bool_not(bool b) { return !b; }

bool bool_equal(bool a, bool b){ return a == b; }
bool bool_not_equal(bool a, bool b){ return a != b; }

bool if_else(bool condition, bool a, bool b){ return condition ? a : b; }

void bvec2_split(bvec2 v, out bool x, out bool y){ x = v.x; y = v.y; }
bvec2 bvec2_join(bool x, bool y){ return bvec2(x,y); }

void bvec3_split(bvec3 v, out bool x, out bool y, out bool z){ x = v.x; y = v.y; z = v.z; }
bvec3 bvec3_join(bool x, bool y, bool z){ return bvec3(x,y,z); }

void bvec4_split(bvec4 v, out bool x, out bool y, out bool z, out bool w){ x = v.x; y = v.y; z = v.z; w = v.w; }
bvec4 bvec4_join(bool x, bool y, bool z, bool w){ return bvec4(x,y,z,w); }

#endif //BOOL_GLSL
