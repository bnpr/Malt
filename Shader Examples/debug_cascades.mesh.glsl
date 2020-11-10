//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

@MAIN_PASS_PIXEL_SHADER
{
    vec3 result = vec3(0,0,0);

    for (int i = 0; i < LIGHTS.lights_count; i++)
    {
        Light light = LIGHTS.lights[i];
        LitSurface surface = lit_surface(POSITION, NORMAL, light);
        if(surface.cascade >= 0)
        {
            result += light.color * (1.0 - (1.0 / SUN_CASCADES) * surface.cascade) * (surface.shadow ? 0 : 1);
        }
    }

    OUT_COLOR = vec4(result, 1.0);
}

