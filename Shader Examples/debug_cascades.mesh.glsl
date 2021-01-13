//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Pipelines/NPR_Pipeline.glsl"


void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(POSITION, NORMAL, light, true);
        if(surface.cascade >= 0)
        {
            result += light.color * (1.0 - (1.0 / SUN_CASCADES) * surface.cascade) * (surface.shadow ? 0 : 1);
        }
    }
    
    PO.color = vec4(result, 1.0);
}

