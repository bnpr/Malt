#ifndef NPR_FILTERS_GLSL
#define NPR_FILTERS_GLSL

#include "Filters/AO.glsl"
#include "Filters/Bevel.glsl"
#include "Filters/Curvature.glsl"
#include "Filters/Line.glsl"

#if defined(PIXEL_SHADER) && (defined(MAIN_PASS) || defined(IS_SCREEN_SHADER))
#define NPR_FILTERS_ACTIVE
#endif

float ao(int samples, float radius)
{
    #ifdef NPR_FILTERS_ACTIVE
    {
        float ao = ao(IN_NORMAL_DEPTH, 3, POSITION, normalize(NORMAL), samples, radius, 5.0, 0);
        ao = pow(ao, 5.0); //Pow for more contrast
        //TODO: For some reason, using pow causes some values to go below 0 ?!?!?!?
        ao = max(0, ao);
        return ao;
    }
    #else
    {
        return 1.0;
    }
    #endif
}

float curvature()
{
    #ifdef NPR_FILTERS_ACTIVE
    {
        vec3 x = transform_normal(inverse(CAMERA), vec3(1,0,0));
        vec3 y = transform_normal(inverse(CAMERA), vec3(0,1,0));
        return curvature(IN_NORMAL_DEPTH, screen_uv(), 1.0, x, y);
    }
    #else
    {
        return 0.5;
    }
    #endif
}

float surface_curvature(float depth_range /*0.5*/)
{
    #ifdef NPR_FILTERS_ACTIVE
    {
        vec3 x = transform_normal(inverse(CAMERA), vec3(1,0,0));
        vec3 y = transform_normal(inverse(CAMERA), vec3(0,1,0));
        return surface_curvature(IN_NORMAL_DEPTH, IN_NORMAL_DEPTH, 3, screen_uv(), 1.0, x, y, depth_range);
    }
    #else
    {
        return 0.5;
    }
    #endif
}

vec3 soft_bevel(int samples, float radius, float distribution_pow, bool only_self)
{
    #ifdef NPR_FILTERS_ACTIVE
    {
        uint id = texture(IN_ID, screen_uv())[0];
        return bevel(
            IN_NORMAL_DEPTH, IN_NORMAL_DEPTH, 3,
            id, only_self, IN_ID, 0,
            samples, radius, distribution_pow,
            false, 1);
    }
    #endif
    return NORMAL;
}

vec3 hard_bevel(int samples, float radius, float distribution_pow, bool only_self, float max_dot)
{
    #ifdef NPR_FILTERS_ACTIVE
    {
        uint id = texture(IN_ID, screen_uv())[0];
        return bevel(
            IN_NORMAL_DEPTH, IN_NORMAL_DEPTH, 3,
            id, only_self, IN_ID, 0,
            samples, radius, distribution_pow,
            true, max_dot);
    }
    #endif
    return NORMAL;
}

LineDetectionOutput line_detection()
{
    LineDetectionOutput result;

    #ifdef NPR_FILTERS_ACTIVE
    {
        result = line_detection(
            POSITION,
            NORMAL, true_normal(),
            1,
            LINE_DEPTH_MODE_NEAR,
            screen_uv(),
            IN_NORMAL_DEPTH,
            3,
            IN_NORMAL_DEPTH,
            IN_ID
        );
    }
    #endif

    return result;
}

void _fix_range(inout float value, inout float range)
{
    if(range < 0)
    {
        range = abs(range);
        value -= range;
    }
}

float line_width(
    float line_width_scale, vec4 id_boundary_width,
    float depth_width, float depth_width_range, float depth_threshold, float depth_threshold_range,
    float normal_width, float normal_width_range, float normal_threshold, float normal_threshold_range
)
{
    #ifdef NPR_FILTERS_ACTIVE
    {
        LineDetectionOutput lo = line_detection();

        float line = 0;

        vec4 id = vec4(lo.id_boundary) * id_boundary_width;
        
        for(int i = 0; i < 4; i++)
        {
            line = max(line, id[i]);
        }

        _fix_range(depth_width, depth_width_range);
        _fix_range(depth_threshold, depth_threshold_range);

        if(lo.delta_distance > depth_threshold)
        {
            float depth = map_range_clamped(
                lo.delta_distance, 
                depth_threshold, depth_threshold + depth_threshold_range,
                depth_width, depth_width + depth_width_range
            );

            line = max(line, depth);
        }

        _fix_range(normal_width, normal_width_range);
        _fix_range(normal_threshold, normal_threshold_range);

        if(lo.delta_angle > normal_threshold)
        {
            float angle = map_range_clamped(
                lo.delta_angle, 
                normal_threshold, normal_threshold + normal_threshold_range,
                normal_width, normal_width + normal_width_range
            );

            line = max(line, angle);
        }

        return line * line_width_scale;
    }
    #else
    {
        return 0.0;
    }
    #endif
}

#endif //NPR_FILTERS_GLSL
