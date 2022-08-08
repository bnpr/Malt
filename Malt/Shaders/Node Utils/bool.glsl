#ifndef BOOL_GLSL
#define BOOL_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Boolean Logic;
*/

/*META @meta: label=And;*/
bool bool_and(bool a, bool b) { return a && b; }
/*META @meta: label=Or;*/
bool bool_or(bool a, bool b) { return a || b; }
/*META @meta: label=Not;*/
bool bool_not(bool b) { return !b; }
/*META @meta: label=Equal;*/
bool bool_equal(bool a, bool b){ return a == b; }
/*META @meta: label=Not Equal;*/
bool bool_not_equal(bool a, bool b){ return a != b; }
/* META @a: label=If True; @b: label=If False; */
bool if_else(bool condition, bool a, bool b){ return condition ? a : b; }

#endif //BOOL_GLSL
