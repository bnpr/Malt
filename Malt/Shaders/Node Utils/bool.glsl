#ifndef BOOL_GLSL
#define BOOL_GLSL

bool bool_and(bool a, bool b) { return a && b; }
bool bool_or(bool a, bool b) { return a || b; }
bool bool_not(bool b) { return !b; }

bool bool_equal(bool a, bool b){ return a == b; }
bool bool_not_equal(bool a, bool b){ return a != b; }

bool if_else(bool condition, bool if_true, bool if_false){ return condition ? if_true : if_false; }

#endif //BOOL_GLSL
