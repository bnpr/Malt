#ifndef NODE_UTILS_COMMON_GLSL
#define NODE_UTILS_COMMON_GLSL

/*  META GLOBAL
    @meta: category=Input; internal=true;
*/

/*META @meta: subcategory=Surface; */
vec3 surface_position() { return POSITION; }
/*META @meta: subcategory=Surface; */
vec3 surface_normal() { return NORMAL; }
/*META @meta: subcategory=Surface; */
vec3 surface_tangent(int index) { return get_tangent(index); }
/*META @meta: subcategory=Surface; */
vec3 surface_bitangent(int index) { return get_bitangent(index); }
/*META @meta: subcategory=Surface; */
vec2 surface_uv(int index) { return UV[index]; }
/*META @meta: subcategory=Surface; */
vec4 surface_vertex_color(int index) { return COLOR[index]; }
/*META @meta: subcategory=Surface; */
vec3 surface_original_position() { return IO_POSITION; }
/*META @meta: subcategory=Surface; */
vec3 surface_original_normal() { return IO_NORMAL; }

uvec4 object_id() { return ID; }
uvec4 object_original_id() { return IO_ID; }

mat4 model_matrix() { return MODEL; }
mat4 camera_matrix() { return CAMERA; }
mat4 projection_matrix() { return PROJECTION; }

vec2 render_resolution() { return vec2(RESOLUTION); }
vec2 sample_offset() { return SAMPLE_OFFSET; }
int sample_count() { return SAMPLE_COUNT; }

int current_frame() { return FRAME; }
float current_time() { return TIME; }

#endif // NODE_UTILS_COMMON_GLSL
