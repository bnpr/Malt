//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#include "Pipelines/NPR_Pipeline.glsl"

uniform vec3 ambient_color = vec3(0.1,0.1,0.1);
uniform vec3 diffuse_color = vec3(1.0,0.1,0.1);
uniform vec3 specular_color = vec3(1.0,1.0,1.0);
uniform float roughness = 0.5;
uniform float alpha = 1.0;

//Expose the setting to the UI
uniform bool cast_shadows = true;

void COMMON_PIXEL_SHADER(Surface S, inout PixelOutput PO)
{
    #if defined(PIXEL_SHADER) && defined(SHADOW_PASS)
    {
        // This code is only executed when rendering shadow maps
        if(cast_shadows == false)
        {
            //Don't draw this
            discard;
        }
    }
    #endif
    

    vec3 diffuse = diffuse_color * get_diffuse_half();
    vec3 specular = specular_color * get_specular(roughness);

    PO.color.rgb = ambient_color + diffuse + specular;
}

