#ifndef COMMON_MAPPING_GLSL
#define COMMON_MAPPING_GLSL

#include "Common.glsl"

/* META GLOBAL
    @meta: category=Vector; internal=True;
*/

vec3 view_direction();
vec3 transform_normal(mat4 matrix, vec3 normal);

/*  META
	@meta: label=Matcap UV;
    @normal: subtype=Normal; default=NORMAL;
*/
vec2 matcap_uv(vec3 normal)
{
	vec3 N = transform_normal(CAMERA, normal);
	vec3 I = transform_normal(CAMERA, -view_direction());

	vec3 x = vec3(1,0,0);
	vec3 tangent = normalize(x - I * dot(x, I));
	vec3 y = vec3(0,1,0);
	vec3 bitangent = normalize(y - I * dot(y, I));
	
	vec3 screen_normal = vec3
	(
		dot(N, tangent),
		dot(N, bitangent),
		dot(N, I)
	);

	screen_normal = normalize(screen_normal);

	return screen_normal.xy * 0.499 + 0.5;
}

/*  META
	@meta: category=Texturing;
    @normal: subtype=Normal; default=NORMAL;
*/
vec4 sample_matcap(sampler2D matcap, vec3 normal)
{
	return textureLod(matcap, matcap_uv(normal), 0);
}

/*  META
	@meta: label=HDRI UV;
    @normal: subtype=Normal; default=NORMAL;
*/
vec2 hdri_uv(vec3 normal)
{
    vec2 uv = vec2(atan(normal.y, normal.x), asin(normal.z));
    vec2 inverse_atan = vec2(0.1591, 0.3183);
    return uv * inverse_atan + 0.5;
}

/*  META
	@meta: category=Texturing; label=Sample HDRI;
    @normal: subtype=Normal; default=NORMAL;
*/
vec4 sample_hdri(sampler2D hdri, vec3 normal)
{
	return textureLod(hdri, hdri_uv(normal), 0);
}

vec2 curve_view_mapping(vec2 uv, vec3 normal, vec3 tangent, vec3 incoming)
{
	vec3 screen_bitangent = transform_normal(CAMERA, cross(incoming, tangent));
	vec3 screen_normal = transform_normal(CAMERA, normal);
	float y_grad = dot(screen_bitangent, screen_normal);
	return vec2(uv.x, (y_grad + 1) * 0.5);
}

vec4 sample_flipbook(sampler2D tex, vec2 uv, ivec2 dimensions, int page)
{
    int page_count = dimensions.x * dimensions.y;
    page = int(mod(page, page_count));
    vec2 offset = vec2(
        mod(page, dimensions.x),
        floor(page / dimensions.y)
    );
    uv = (uv + offset) / vec2(dimensions);
    return texture(tex, uv);
}

float pingpong(float a, float b);

vec4 flowmap(sampler2D tex, vec2 uv, vec2 flow, float progression, int samples)
{
    vec4 result;
    float fraction = 1.0 / float(samples);
    for(int i = 0; i < samples; i++)
    {
        float flow_scale = fract(progression - i * fraction);
        vec4 color = texture(tex, uv - flow * flow_scale);

        float range = fract(progression - (float(i) / float(samples))) * samples;
        float p = pingpong(range, 1.0);
        float bounds = (range > 0.0 && range < 2.0)? 1.0 : 0.0;
        result += color * p * bounds;
    }
    return result;
}

#endif //COMMON_MAPPING_GLSL
