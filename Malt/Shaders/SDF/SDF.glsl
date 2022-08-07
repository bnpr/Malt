#ifndef SDF_SDF_GLSL
#define SDF_SDF_GLSL

#include "Common/Transform.glsl"

// SDF functions adapted from https://www.iquilezles.org/www/articles/distfunctions/distfunctions.htm

/* META GLOBAL
    @meta: internal=true;
*/

float sdf_box(vec3 p, vec3 size)
{
    vec3 q = abs(p) - (size / 2.0);
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
}

float sdf_sphere(vec3 p, float radius)
{
    return length(p) - radius;
}

float sdf_ellipsoid(vec3 p, vec3 radius)
{
    float k0 = length(p / radius);
    float k1 = length(p / (radius * radius));
    return k0 * (k0 - 1.0) / k1;
}

float sdf_cone(vec3 p, float radius, float height)
{
    vec2 q = vec2(radius, -height);
    vec2 w = vec2(length(p.xy), p.z - height);
    vec2 a = w - (q * clamp(dot(w, q) / dot(q, q), 0.0, 1.0));
    vec2 b = w - (q * vec2(clamp(w.x / q.x, 0.0, 1.0), 1.0));
    float k = sign(q.y);
    float d = min(dot(a, a),dot(b, b));
    float s = max(k * ((w.x * q.y) - (w.y * q.x)), k * (w.y - q.y));
    return sqrt(d) * sign(s);
}

float sdf_capsule(vec3 p, vec3 a, vec3 b, float radius)
{
    vec3 pa = p - a;
    vec3 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - (ba * h)) - radius;
}

float sdf_smooth(float a, float radius) { return a - radius; }

float sdf_union(float a, float b) { return min(a, b); }

float sdf_difference(float a, float b) { return max(a, -b); }

float sdf_intersection(float a, float b) { return max(a, b); }

float sdf_union_smooth(float a, float b, float smooth_size)
{
    float h = clamp(0.5 + 0.5 * (b - a) / smooth_size, 0.0, 1.0);
    return mix(b, a, h) - smooth_size * h * (1.0 - h);
}

float sdf_difference_smooth(float a, float b, float smooth_size)
{
    float h = clamp(0.5 - 0.5 * (b + a) / smooth_size, 0.0, 1.0);
    return mix(a, -b, h) + smooth_size * h * (1.0 - h);
}

float sdf_intersection_smooth(float a, float b, float smooth_size)
{
    float h = clamp(0.5 - 0.5 * (b - a) / smooth_size, 0.0, 1.0);
    return mix(b, a, h) + smooth_size * h * (1.0 - h);
}

struct RayMarchResult
{
    bool hit;
    int step;
    float depth;
    vec3 position;
    vec3 normal;
};

float scene_sdf(vec3 p);

// To include this file and call this function you must define your own scene_sdf function
RayMarchResult raymarch_scene(vec3 ray_start, vec3 ray_end, int max_steps, float min_precision)
{
    RayMarchResult r = RayMarchResult(false, 0, 0, vec3(0), vec3(0));
    vec3 ray = normalize(ray_end - ray_start);
    float ray_length = distance(ray_start, ray_end);
    
    for (r.step = 0; r.step < max_steps; r.step++)
    {
        float signed_distance = scene_sdf(ray_start + min(r.depth, ray_length) * ray);
        if (signed_distance < min_precision)
        {
            break;
        }
        if (r.depth > ray_length)
        {
            return r;
        }
        r.depth += signed_distance;
    }
    
    r.hit = true;
    r.position = ray_start + r.depth * ray;
    float projected_depth = project_point(PROJECTION * CAMERA, r.position).z;
    float offset_scale = pixel_world_size_at(projected_depth);
    // https://www.iquilezles.org/www/articles/normalsSDF/normalsSDF.htm
    vec2 k = vec2(1,-1);
    r.normal = normalize
    (
        k.xyy * scene_sdf(r.position + k.xyy * offset_scale) + 
        k.yyx * scene_sdf(r.position + k.yyx * offset_scale) + 
        k.yxy * scene_sdf(r.position + k.yxy * offset_scale) + 
        k.xxx * scene_sdf(r.position + k.xxx * offset_scale)
    );
    
    return r;
}

#endif //SDF_SDF_GLSL
