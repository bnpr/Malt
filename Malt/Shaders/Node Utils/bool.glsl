// bool
bool bool_property(bool b) { return b; }
bool bool_true() { return true; } 
bool bool_false() { return false; }

bool bool_and(bool a, bool b) { return a && b; }
bool bool_or(bool a, bool b) { return a || b; }
bool bool_not(bool b) { return !b; }

bool bool_equal(bool a, bool b){ return a == b; }
bool bool_not_equal(bool a, bool b){ return a != b; }

bool if_else(bool condition, bool a, bool b){ return condition ? a : b; }

