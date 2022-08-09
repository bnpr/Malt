#ifndef NODE_UTILS_2_BOOL_GLSL
#define NODE_UTILS_2_BOOL_GLSL

/*  META GLOBAL
    @meta: category=Math; subcategory=Boolean Logic;
*/

/*META @meta: label=And;*/
bool Bool_and(bool a, bool b) { return a && b; }
/*META @meta: label=Or;*/
bool Bool_or(bool a, bool b) { return a || b; }
/*META @meta: label=Not;*/
bool Bool_not(bool b) { return !b; }
/*META @meta: label=Equal;*/
bool Bool_equal(bool a, bool b){ return a == b; }
/*META @meta: label=Not Equal;*/
bool Bool_not_equal(bool a, bool b){ return a != b; }
/*META @meta: label=If Else; @a: label=If True; @b: label=If False; */
bool Bool_if_else(bool condition, bool a, bool b){ return condition ? a : b; }

#endif //NODE_UTILS_2_BOOL_GLSL
