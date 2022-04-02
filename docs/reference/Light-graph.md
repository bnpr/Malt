# Light Graph Reference
---
## Common - Color
---
### **alpha_blend**
>vec4 alpha_blend(vec4 base, vec4 blend)

Blends the blend color as a layer over the base color.

- **Inputs**  
	- **base** *: ( vec4 )*  
	- **blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	>The blend color.
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **relative_luminance**
>float relative_luminance(vec3 color)

- **Inputs**  
	- **color** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **luma**
>float luma(vec3 color)

- **Inputs**  
	- **color** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **linear_to_srgb**
>vec3 linear_to_srgb(vec3 linear)

- **Inputs**  
	- **linear** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **srgb_to_linear**
>vec3 srgb_to_linear(vec3 srgb)

- **Inputs**  
	- **srgb** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **rgb_to_hsv**
>vec3 rgb_to_hsv(vec3 rgb)

- **Inputs**  
	- **rgb** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **hsv_to_rgb**
>vec3 hsv_to_rgb(vec3 hsv)

- **Inputs**  
	- **hsv** *: ( vec3 | HSV )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **hsv_edit**
>vec4 hsv_edit(vec4 color, float hue, float saturation, float value)

- **Inputs**  
	- **color** *: ( vec4 )*  
	- **hue** *: ( float )*  
	- **saturation** *: ( float )*  
	- **value** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **rgb_gradient**
>vec3 rgb_gradient(sampler1D gradient, vec3 uvw)

- **Inputs**  
	- **gradient** *: ( sampler1D )*  
	- **uvw** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **rgba_gradient**
>vec4 rgba_gradient(sampler1D gradient, vec4 uvw)

- **Inputs**  
	- **gradient** *: ( sampler1D )*  
	- **uvw** *: ( vec4 )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
## Common - Hash - hash
---
### **hash**
>vec4 hash(float v)

- **Inputs**  
	- **v** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **hash**
>vec4 hash(vec2 v)

- **Inputs**  
	- **v** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **hash**
>vec4 hash(vec3 v)

- **Inputs**  
	- **v** *: ( vec3 | Data )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **hash**
>vec4 hash(vec4 v)

- **Inputs**  
	- **v** *: ( vec4 | Data )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
## Common - Mapping
---
### **matcap_uv**
>vec2 matcap_uv(vec3 normal)

- **Inputs**  
	- **normal** *: ( vec3 | Normal ) - default = NORMAL*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **sample_matcap**
>vec4 sample_matcap(sampler2D matcap, vec3 normal)

- **Inputs**  
	- **matcap** *: ( sampler2D )*  
	- **normal** *: ( vec3 | Normal ) - default = NORMAL*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **hdri_uv**
>vec2 hdri_uv(vec3 normal)

- **Inputs**  
	- **normal** *: ( vec3 | Normal ) - default = NORMAL*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **sample_hdri**
>vec4 sample_hdri(sampler2D hdri, vec3 normal)

- **Inputs**  
	- **hdri** *: ( sampler2D )*  
	- **normal** *: ( vec3 | Normal ) - default = NORMAL*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
## Common - Math
---
### **random_per_sample**
>vec4 random_per_sample(float seed)

- **Inputs**  
	- **seed** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **random_per_pixel**
>vec4 random_per_pixel(float seed)

- **Inputs**  
	- **seed** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
## Common - Quaternion
---
### **quaternion_from_axis_angle**
>vec4 quaternion_from_axis_angle(vec3 axis, float angle)

- **Inputs**  
	- **axis** *: ( vec3 | Normal )*  
	- **angle** *: ( float | Angle )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **quaternion_from_vector_delta**
>vec4 quaternion_from_vector_delta(vec3 from, vec3 to)

- **Inputs**  
	- **from** *: ( vec3 | Normal )*  
	- **to** *: ( vec3 | Normal )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **quaternion_inverted**
>vec4 quaternion_inverted(vec4 quaternion)

- **Inputs**  
	- **quaternion** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **quaternion_multiply**
>vec4 quaternion_multiply(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
	- **b** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **quaternion_transform**
>vec3 quaternion_transform(vec4 quaternion, vec3 vector)

- **Inputs**  
	- **quaternion** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
	- **vector** *: ( vec3 | Vector ) - default = (0.0, 0.0, 0.0)*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **quaternion_mix**
>vec4 quaternion_mix(vec4 a, vec4 b, float factor)

- **Inputs**  
	- **a** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
	- **b** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
	- **factor** *: ( float | Slider ) - default = 0.5*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
## Common - Matrix
---
### **mat4_translation**
>mat4 mat4_translation(vec3 t)

- **Inputs**  
	- **t** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( mat4 )*  
---
### **mat4_rotation_from_quaternion**
>mat4 mat4_rotation_from_quaternion(vec4 q)

- **Inputs**  
	- **q** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
- **Outputs**  
	- **result** *: ( mat4 )*  
---
### **mat4_rotation_from_euler**
>mat4 mat4_rotation_from_euler(vec3 e)

- **Inputs**  
	- **e** *: ( vec3 | Euler )*  
- **Outputs**  
	- **result** *: ( mat4 )*  
---
### **mat4_scale**
>mat4 mat4_scale(vec3 s)

- **Inputs**  
	- **s** *: ( vec3 | Vector ) - default = (1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( mat4 )*  
---
### **is_ortho**
>bool is_ortho(mat4 matrix)

- **Inputs**  
	- **matrix** *: ( mat4 ) - default = mat4(1)*  
- **Outputs**  
	- **result** *: ( bool )*  
---
## Common - Normal
---
### **true_normal**
>vec3 true_normal()

- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **facing**
>float facing()

- **Outputs**  
	- **result** *: ( float )*  
---
### **is_front_facing**
>bool is_front_facing()

- **Outputs**  
	- **result** *: ( bool )*  
---
### **compute_tangent**
>vec4 compute_tangent(vec2 uv)

- **Inputs**  
	- **uv** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **get_tangent**
>vec3 get_tangent(int uv_index)

- **Inputs**  
	- **uv_index** *: ( int )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **get_bitangent**
>vec3 get_bitangent(int uv_index)

- **Inputs**  
	- **uv_index** *: ( int )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **get_TBN**
>mat3 get_TBN(int uv_index)

- **Inputs**  
	- **uv_index** *: ( int )*  
- **Outputs**  
	- **result** *: ( mat3 )*  
---
### **sample_normal_map_ex**
>vec3 sample_normal_map_ex(sampler2D normal_texture, mat3 TBN, vec2 uv)

- **Inputs**  
	- **normal_texture** *: ( sampler2D )*  
	- **TBN** *: ( mat3 )*  
	- **uv** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **sample_normal_map**
>vec3 sample_normal_map(sampler2D normal_texture, int uv_index, vec2 uv)

- **Inputs**  
	- **normal_texture** *: ( sampler2D )*  
	- **uv_index** *: ( int )*  
	- **uv** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **radial_tangent**
>vec3 radial_tangent(vec3 normal, vec3 axis)

- **Inputs**  
	- **normal** *: ( vec3 | Normal ) - default = NORMAL*  
	- **axis** *: ( vec3 | Normal ) - default = (0, 0, 1)*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **surface_gradient_from_normal**
>vec3 surface_gradient_from_normal(vec3 custom_normal)

- **Inputs**  
	- **custom_normal** *: ( vec3 | Normal ) - default = NORMAL*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **normal_from_surface_gradient**
>vec3 normal_from_surface_gradient(vec3 surface_gradient)

- **Inputs**  
	- **surface_gradient** *: ( vec3 | Vector ) - default = (0.0, 0.0, 0.0)*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
## Common - Transform
---
### **transform_point**
>vec3 transform_point(mat4 matrix, vec3 point)

- **Inputs**  
	- **matrix** *: ( mat4 ) - default = mat4(1)*  
	- **point** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **project_point**
>vec3 project_point(mat4 matrix, vec3 point)

- **Inputs**  
	- **matrix** *: ( mat4 ) - default = mat4(1)*  
	- **point** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **transform_direction**
>vec3 transform_direction(mat4 matrix, vec3 direction)

- **Inputs**  
	- **matrix** *: ( mat4 ) - default = mat4(1)*  
	- **direction** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **transform_normal**
>vec3 transform_normal(mat4 matrix, vec3 normal)

- **Inputs**  
	- **matrix** *: ( mat4 ) - default = mat4(1)*  
	- **normal** *: ( vec3 | Normal )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **camera_position**
>vec3 camera_position()

- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **model_position**
>vec3 model_position()

- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **screen_uv**
>vec2 screen_uv()

- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **screen_pixel**
>ivec2 screen_pixel()

- **Outputs**  
	- **result** *: ( ivec2 )*  
---
### **screen_to_camera**
>vec3 screen_to_camera(vec2 uv, float depth)

- **Inputs**  
	- **uv** *: ( vec2 )*  
	- **depth** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **view_direction**
>vec3 view_direction()

- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **pixel_depth**
>float pixel_depth()

- **Outputs**  
	- **result** *: ( float )*  
---
### **depth_to_z**
>float depth_to_z(float depth)

- **Inputs**  
	- **depth** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **pixel_world_size_at**
>float pixel_world_size_at(float depth)

- **Inputs**  
	- **depth** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **pixel_world_size**
>float pixel_world_size()

- **Outputs**  
	- **result** *: ( float )*  
---
### **ray_plane_intersection**
>float ray_plane_intersection(vec3 ray_origin, vec3 ray_direction, vec3 plane_position, vec3 plane_normal)

- **Inputs**  
	- **ray_origin** *: ( vec3 | Vector )*  
	- **ray_direction** *: ( vec3 | Vector )*  
	- **plane_position** *: ( vec3 | Vector )*  
	- **plane_normal** *: ( vec3 | Normal )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **rotate_2d**
>vec2 rotate_2d(vec2 p, float angle)

- **Inputs**  
	- **p** *: ( vec2 )*  
	- **angle** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
## Node Utils - common
---
### **surface_position**
>vec3 surface_position()

- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **surface_normal**
>vec3 surface_normal()

- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **surface_tangent**
>vec3 surface_tangent(int index)

- **Inputs**  
	- **index** *: ( int )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **surface_bitangent**
>vec3 surface_bitangent(int index)

- **Inputs**  
	- **index** *: ( int )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **surface_uv**
>vec2 surface_uv(int index)

- **Inputs**  
	- **index** *: ( int )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **surface_vertex_color**
>vec4 surface_vertex_color(int index)

- **Inputs**  
	- **index** *: ( int )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **object_id**
>uvec4 object_id()

- **Outputs**  
	- **result** *: ( uvec4 )*  
---
### **model_matrix**
>mat4 model_matrix()

- **Outputs**  
	- **result** *: ( mat4 )*  
---
### **camera_matrix**
>mat4 camera_matrix()

- **Outputs**  
	- **result** *: ( mat4 )*  
---
### **projection_matrix**
>mat4 projection_matrix()

- **Outputs**  
	- **result** *: ( mat4 )*  
---
### **render_resolution**
>vec2 render_resolution()

- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **sample_offset**
>vec2 sample_offset()

- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **sample_count**
>int sample_count()

- **Outputs**  
	- **result** *: ( int )*  
---
### **current_frame**
>int current_frame()

- **Outputs**  
	- **result** *: ( int )*  
---
### **current_time**
>float current_time()

- **Outputs**  
	- **result** *: ( float )*  
---
## Node Utils - bool
---
### **bool_and**
>bool bool_and(bool a, bool b)

- **Inputs**  
	- **a** *: ( bool )*  
	- **b** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **bool_or**
>bool bool_or(bool a, bool b)

- **Inputs**  
	- **a** *: ( bool )*  
	- **b** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **bool_not**
>bool bool_not(bool b)

- **Inputs**  
	- **b** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **bool_equal**
>bool bool_equal(bool a, bool b)

- **Inputs**  
	- **a** *: ( bool )*  
	- **b** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **bool_not_equal**
>bool bool_not_equal(bool a, bool b)

- **Inputs**  
	- **a** *: ( bool )*  
	- **b** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **if_else**
>bool if_else(bool condition, bool if_true, bool if_false)

- **Inputs**  
	- **condition** *: ( bool )*  
	- **if_true** *: ( bool )*  
	- **if_false** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
## Node Utils - float
---
### **float_add**
>float float_add(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_subtract**
>float float_subtract(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_multiply**
>float float_multiply(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_divide**
>float float_divide(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_modulo**
>float float_modulo(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_pow**
>float float_pow(float f, float e)

- **Inputs**  
	- **f** *: ( float )*  
	- **e** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_sqrt**
>float float_sqrt(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_round**
>float float_round(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_fract**
>float float_fract(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_floor**
>float float_floor(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_ceil**
>float float_ceil(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_clamp**
>float float_clamp(float f, float min, float max)

- **Inputs**  
	- **f** *: ( float )*  
	- **min** *: ( float )*  
	- **max** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_sign**
>float float_sign(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_abs**
>float float_abs(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_min**
>float float_min(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_max**
>float float_max(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_mix**
>float float_mix(float a, float b, float factor)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
	- **factor** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_sin**
>float float_sin(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_cos**
>float float_cos(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_tan**
>float float_tan(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_asin**
>float float_asin(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_acos**
>float float_acos(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_atan**
>float float_atan(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_degrees**
>float float_degrees(float r)

- **Inputs**  
	- **r** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_radians**
>float float_radians(float d)

- **Inputs**  
	- **d** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **float_equal**
>bool float_equal(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **float_not_equal**
>bool float_not_equal(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **float_greater**
>bool float_greater(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **float_greater_or_equal**
>bool float_greater_or_equal(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **float_less**
>bool float_less(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **float_less_or_equal**
>bool float_less_or_equal(float a, float b)

- **Inputs**  
	- **a** *: ( float )*  
	- **b** *: ( float )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **float_if_else**
>float float_if_else(bool condition, float if_true, float if_false)

- **Inputs**  
	- **condition** *: ( bool )*  
	- **if_true** *: ( float )*  
	- **if_false** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
## Node Utils - int
---
### **int_add**
>int int_add(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **int_subtract**
>int int_subtract(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **int_multiply**
>int int_multiply(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **int_divide**
>int int_divide(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **int_modulo**
>int int_modulo(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **int_clamp**
>int int_clamp(int i, int min, int max)

- **Inputs**  
	- **i** *: ( int )*  
	- **min** *: ( int )*  
	- **max** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **int_sign**
>int int_sign(int i)

- **Inputs**  
	- **i** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **int_abs**
>int int_abs(int i)

- **Inputs**  
	- **i** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **int_min**
>int int_min(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **int_max**
>int int_max(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **int_equal**
>bool int_equal(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **int_not_equal**
>bool int_not_equal(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **int_greater**
>bool int_greater(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **int_greater_or_equal**
>bool int_greater_or_equal(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **int_less**
>bool int_less(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **int_less_or_equal**
>bool int_less_or_equal(int a, int b)

- **Inputs**  
	- **a** *: ( int )*  
	- **b** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **int_if_else**
>int int_if_else(bool condition, int if_true, int if_false)

- **Inputs**  
	- **condition** *: ( bool )*  
	- **if_true** *: ( int )*  
	- **if_false** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
## Node Utils - packing
---
### **pack_8bit**
>uvec4 pack_8bit(vec4 a, vec4 b, vec4 c, vec4 d)

- **Inputs**  
	- **a** *: ( vec4 )*  
	- **b** *: ( vec4 )*  
	- **c** *: ( vec4 )*  
	- **d** *: ( vec4 )*  
- **Outputs**  
	- **result** *: ( uvec4 )*  
---
### **unpack_8bit**
>void unpack_8bit(uvec4 packed_vector, out vec4 a, out vec4 b, out vec4 c, out vec4 d)

- **Inputs**  
	- **packed_vector** *: ( uvec4 )*  
- **Outputs**  
	- **a** *: ( vec4 )*  
	- **b** *: ( vec4 )*  
	- **c** *: ( vec4 )*  
	- **d** *: ( vec4 )*  
---
## Node Utils - properties
---
### **bool_property**
>bool bool_property(bool b)

- **Inputs**  
	- **b** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **float_property**
>float float_property(float f)

- **Inputs**  
	- **f** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **int_property**
>int int_property(int i)

- **Inputs**  
	- **i** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **vec2_property**
>vec2 vec2_property(vec2 v)

- **Inputs**  
	- **v** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec3_property**
>vec3 vec3_property(vec3 v)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec4_property**
>vec4 vec4_property(vec4 v)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec3_color_property**
>vec3 vec3_color_property(vec3 v)

- **Inputs**  
	- **v** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec4_color_property**
>vec4 vec4_color_property(vec4 v)

- **Inputs**  
	- **v** *: ( vec4 )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
## Node Utils - sampler
---
### **sampler1D_sample**
>vec4 sampler1D_sample(sampler1D t, float u)

- **Inputs**  
	- **t** *: ( sampler1D )*  
	- **u** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **sampler1D_size**
>int sampler1D_size(sampler1D t)

- **Inputs**  
	- **t** *: ( sampler1D )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **sampler1D_textel_fetch**
>vec4 sampler1D_textel_fetch(sampler1D t, int u)

- **Inputs**  
	- **t** *: ( sampler1D )*  
	- **u** *: ( int )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **sampler2D_sample**
>vec4 sampler2D_sample(sampler2D t, vec2 uv)

- **Inputs**  
	- **t** *: ( sampler2D )*  
	- **uv** *: ( vec2 ) - default = UV[0]*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **sampler2D_sample_nearest**
>vec4 sampler2D_sample_nearest(sampler2D t, vec2 uv)

- **Inputs**  
	- **t** *: ( sampler2D )*  
	- **uv** *: ( vec2 ) - default = UV[0]*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **sampler2D_size**
>ivec2 sampler2D_size(sampler2D t)

- **Inputs**  
	- **t** *: ( sampler2D )*  
- **Outputs**  
	- **result** *: ( ivec2 )*  
---
### **sampler2D_textel_fetch**
>vec4 sampler2D_textel_fetch(sampler2D t, ivec2 uv)

- **Inputs**  
	- **t** *: ( sampler2D )*  
	- **uv** *: ( ivec2 )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
## Node Utils - vec2
---
### **vec2_add**
>vec2 vec2_add(vec2 a, vec2 b)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_subtract**
>vec2 vec2_subtract(vec2 a, vec2 b)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_multiply**
>vec2 vec2_multiply(vec2 a, vec2 b)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_divide**
>vec2 vec2_divide(vec2 a, vec2 b)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_scale**
>vec2 vec2_scale(vec2 v, float s)

- **Inputs**  
	- **v** *: ( vec2 )*  
	- **s** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_modulo**
>vec2 vec2_modulo(vec2 a, vec2 b)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_pow**
>vec2 vec2_pow(vec2 v, vec2 e)

- **Inputs**  
	- **v** *: ( vec2 )*  
	- **e** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_sqrt**
>vec2 vec2_sqrt(vec2 v)

- **Inputs**  
	- **v** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_round**
>vec2 vec2_round(vec2 v)

- **Inputs**  
	- **v** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_fract**
>vec2 vec2_fract(vec2 v)

- **Inputs**  
	- **v** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_floor**
>vec2 vec2_floor(vec2 v)

- **Inputs**  
	- **v** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_ceil**
>vec2 vec2_ceil(vec2 v)

- **Inputs**  
	- **v** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_clamp**
>vec2 vec2_clamp(vec2 v, vec2 min, vec2 max)

- **Inputs**  
	- **v** *: ( vec2 )*  
	- **min** *: ( vec2 )*  
	- **max** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_sign**
>vec2 vec2_sign(vec2 v)

- **Inputs**  
	- **v** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_abs**
>vec2 vec2_abs(vec2 v)

- **Inputs**  
	- **v** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_min**
>vec2 vec2_min(vec2 a, vec2 b)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_max**
>vec2 vec2_max(vec2 a, vec2 b)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_mix**
>vec2 vec2_mix(vec2 a, vec2 b, vec2 factor)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
	- **factor** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_mix_float**
>vec2 vec2_mix_float(vec2 a, vec2 b, float factor)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
	- **factor** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_length**
>float vec2_length(vec2 v)

- **Inputs**  
	- **v** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **vec2_distance**
>float vec2_distance(vec2 a, vec2 b)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **vec2_dot_product**
>float vec2_dot_product(vec2 a, vec2 b)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **vec2_equal**
>bool vec2_equal(vec2 a, vec2 b)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **vec2_not_equal**
>bool vec2_not_equal(vec2 a, vec2 b)

- **Inputs**  
	- **a** *: ( vec2 )*  
	- **b** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **vec2_if_else**
>vec2 vec2_if_else(bool condition, vec2 if_true, vec2 if_false)

- **Inputs**  
	- **condition** *: ( bool )*  
	- **if_true** *: ( vec2 )*  
	- **if_false** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_join**
>vec2 vec2_join(float x, float y)

- **Inputs**  
	- **x** *: ( float )*  
	- **y** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **vec2_split**
>void vec2_split(vec2 v, out float x, out float y)

- **Inputs**  
	- **v** *: ( vec2 )*  
- **Outputs**  
	- **x** *: ( float )*  
	- **y** *: ( float )*  
---
## Node Utils - vec3
---
### **vec3_add**
>vec3 vec3_add(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_subtract**
>vec3 vec3_subtract(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_multiply**
>vec3 vec3_multiply(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_divide**
>vec3 vec3_divide(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_scale**
>vec3 vec3_scale(vec3 v, float s)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
	- **s** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_modulo**
>vec3 vec3_modulo(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_pow**
>vec3 vec3_pow(vec3 v, vec3 e)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
	- **e** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_sqrt**
>vec3 vec3_sqrt(vec3 v)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_round**
>vec3 vec3_round(vec3 v)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_fract**
>vec3 vec3_fract(vec3 v)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_floor**
>vec3 vec3_floor(vec3 v)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_ceil**
>vec3 vec3_ceil(vec3 v)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_clamp**
>vec3 vec3_clamp(vec3 v, vec3 min, vec3 max)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
	- **min** *: ( vec3 | Vector )*  
	- **max** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_sign**
>vec3 vec3_sign(vec3 v)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_abs**
>vec3 vec3_abs(vec3 v)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_min**
>vec3 vec3_min(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_max**
>vec3 vec3_max(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_mix**
>vec3 vec3_mix(vec3 a, vec3 b, vec3 factor)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
	- **factor** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_mix_float**
>vec3 vec3_mix_float(vec3 a, vec3 b, float factor)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
	- **factor** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_length**
>float vec3_length(vec3 v)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **vec3_distance**
>float vec3_distance(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **vec3_dot_product**
>float vec3_dot_product(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **vec3_cross_product**
>vec3 vec3_cross_product(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_equal**
>bool vec3_equal(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **vec3_not_equal**
>bool vec3_not_equal(vec3 a, vec3 b)

- **Inputs**  
	- **a** *: ( vec3 | Vector )*  
	- **b** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **vec3_if_else**
>vec3 vec3_if_else(bool condition, vec3 if_true, vec3 if_false)

- **Inputs**  
	- **condition** *: ( bool )*  
	- **if_true** *: ( vec3 | Vector )*  
	- **if_false** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_join**
>vec3 vec3_join(float x, float y, float z)

- **Inputs**  
	- **x** *: ( float )*  
	- **y** *: ( float )*  
	- **z** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **vec3_split**
>void vec3_split(vec3 v, out float x, out float y, out float z)

- **Inputs**  
	- **v** *: ( vec3 | Vector )*  
- **Outputs**  
	- **x** *: ( float )*  
	- **y** *: ( float )*  
	- **z** *: ( float )*  
---
## Node Utils - vec4
---
### **vec4_add**
>vec4 vec4_add(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_subtract**
>vec4 vec4_subtract(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_multiply**
>vec4 vec4_multiply(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_divide**
>vec4 vec4_divide(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_scale**
>vec4 vec4_scale(vec4 v, float s)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
	- **s** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_modulo**
>vec4 vec4_modulo(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_pow**
>vec4 vec4_pow(vec4 v, vec4 e)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
	- **e** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_sqrt**
>vec4 vec4_sqrt(vec4 v)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_round**
>vec4 vec4_round(vec4 v)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_fract**
>vec4 vec4_fract(vec4 v)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_floor**
>vec4 vec4_floor(vec4 v)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_ceil**
>vec4 vec4_ceil(vec4 v)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_clamp**
>vec4 vec4_clamp(vec4 v, vec4 min, vec4 max)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
	- **min** *: ( vec4 | Vector )*  
	- **max** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_sign**
>vec4 vec4_sign(vec4 v)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_abs**
>vec4 vec4_abs(vec4 v)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_min**
>vec4 vec4_min(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_max**
>vec4 vec4_max(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_mix**
>vec4 vec4_mix(vec4 a, vec4 b, vec4 factor)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
	- **factor** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_mix_float**
>vec4 vec4_mix_float(vec4 a, vec4 b, float factor)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
	- **factor** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_length**
>float vec4_length(vec4 v)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **vec4_distance**
>float vec4_distance(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **vec4_dot_product**
>float vec4_dot_product(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **vec4_equal**
>bool vec4_equal(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **vec4_not_equal**
>bool vec4_not_equal(vec4 a, vec4 b)

- **Inputs**  
	- **a** *: ( vec4 | Vector )*  
	- **b** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **vec4_if_else**
>vec4 vec4_if_else(bool condition, vec4 if_true, vec4 if_false)

- **Inputs**  
	- **condition** *: ( bool )*  
	- **if_true** *: ( vec4 | Vector )*  
	- **if_false** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_join**
>vec4 vec4_join(float r, float g, float b, float a)

- **Inputs**  
	- **r** *: ( float )*  
	- **g** *: ( float )*  
	- **b** *: ( float )*  
	- **a** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **vec4_split**
>void vec4_split(vec4 v, out float r, out float g, out float b, out float a)

- **Inputs**  
	- **v** *: ( vec4 | Vector )*  
- **Outputs**  
	- **r** *: ( float )*  
	- **g** *: ( float )*  
	- **b** *: ( float )*  
	- **a** *: ( float )*  
---
## Filters - Blur
---
### **box_blur**
>vec4 box_blur(sampler2D input_texture, vec2 uv, float radius, bool circular)

- **Inputs**  
	- **input_texture** *: ( sampler2D )*  
	- **uv** *: ( vec2 ) - default = screen_uv()*  
	- **radius** *: ( float ) - default = 5.0*  
	- **circular** *: ( bool )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **gaussian_blur**
>vec4 gaussian_blur(sampler2D input_texture, vec2 uv, float radius, float sigma)

- **Inputs**  
	- **input_texture** *: ( sampler2D )*  
	- **uv** *: ( vec2 ) - default = screen_uv()*  
	- **radius** *: ( float ) - default = 5.0*  
	- **sigma** *: ( float ) - default = 1.0*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **jitter_blur**
>vec4 jitter_blur(sampler2D input_texture, vec2 uv, float radius, float distribution_exponent, int samples)

- **Inputs**  
	- **input_texture** *: ( sampler2D )*  
	- **uv** *: ( vec2 ) - default = screen_uv()*  
	- **radius** *: ( float ) - default = 5.0*  
	- **distribution_exponent** *: ( float ) - default = 5.0*  
	- **samples** *: ( int ) - default = 8*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
## Filters - Curvature
---
### **curvature**
>float curvature(sampler2D normal_texture, vec2 uv, float width, vec3 x, vec3 y)

- **Inputs**  
	- **normal_texture** *: ( sampler2D )*  
	- **uv** *: ( vec2 )*  
	- **width** *: ( float )*  
	- **x** *: ( vec3 )*  
	- **y** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( float )*  
---
## Procedural - Noise
---
### **noise_ex**
>vec4 noise_ex(vec4 coord, bool tile, vec4 tile_size)

- **Inputs**  
	- **coord** *: ( vec4 | Vector ) - default = vec4(POSITION,0)*  
	- **tile** *: ( bool )*  
	- **tile_size** *: ( vec4 | Vector ) - default = (1.0, 1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **noise**
>vec4 noise(vec4 coord)

- **Inputs**  
	- **coord** *: ( vec4 | Vector ) - default = vec4(POSITION,0)*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
## Procedural - Cell_Noise
---
### **cell_noise_ex**
>CellNoiseResult cell_noise_ex(vec4 coord, bool tile, vec4 tile_size)

- **Inputs**  
	- **coord** *: ( vec4 | Vector ) - default = vec4(POSITION,0)*  
	- **tile** *: ( bool )*  
	- **tile_size** *: ( vec4 | Vector ) - default = (1.0, 1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( CellNoiseResult )*  
---
### **cell_noise**
>CellNoiseResult cell_noise(vec4 coord)

- **Inputs**  
	- **coord** *: ( vec4 | Vector ) - default = vec4(POSITION,0)*  
- **Outputs**  
	- **result** *: ( CellNoiseResult )*  
---
## Procedural - Fractal_Noise
---
### **fractal_noise_ex**
>vec4 fractal_noise_ex(vec4 coord, int octaves, bool tile, vec4 tile_size)

- **Inputs**  
	- **coord** *: ( vec4 | Vector ) - default = vec4(POSITION,0)*  
	- **octaves** *: ( int ) - default = 3*  
	- **tile** *: ( bool )*  
	- **tile_size** *: ( vec4 | Vector ) - default = (1.0, 1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **fractal_noise**
>vec4 fractal_noise(vec4 coord, int octaves)

- **Inputs**  
	- **coord** *: ( vec4 | Vector ) - default = vec4(POSITION,0)*  
	- **octaves** *: ( int ) - default = 3*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
## Shading - ShadingModels
---
### **rim_light**
>float rim_light(vec3 normal, float angle, float rim_length, float length_falloff, float thickness, float thickness_falloff)

- **Inputs**  
	- **normal** *: ( vec3 | Normal ) - default = NORMAL*  
	- **angle** *: ( float )*  
	- **rim_length** *: ( float ) - default = 2.0*  
	- **length_falloff** *: ( float )*  
	- **thickness** *: ( float ) - default = 0.1*  
	- **thickness_falloff** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
