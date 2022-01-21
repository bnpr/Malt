#include "NPR_Intellisense.glsl"
#include "Common.glsl"
#include "Lighting/Lighting.glsl"

uniform int LIGHT_INDEX;

struct LightShaderInput
{
    Light L;
    LitSurface LS;
    vec3 light_space_position;
    vec3 light_uv;
};

struct LightShaderOutput
{
    vec3 color;
};

#ifdef VERTEX_SHADER
void main()
{
    DEFAULT_SCREEN_VERTEX_SHADER();
}
#endif

#ifdef PIXEL_SHADER

uniform sampler2D IN_DEPTH;

layout (location = 0) out vec3 RESULT;

void LIGHT_SHADER(LightShaderInput I, inout LightShaderOutput O);

void main()
{
    PIXEL_SETUP_INPUT();

    float depth = texelFetch(IN_DEPTH, screen_pixel(), 0).x;
    POSITION = screen_to_camera(screen_uv(), depth);
    POSITION = transform_point(inverse(CAMERA), POSITION);

    Light L = LIGHTS.lights[LIGHT_INDEX];
    LitSurface LS = lit_surface(POSITION, vec3(0), L, false);
    
    vec3 light_space;
    vec3 light_uv;

    if(L.type == LIGHT_SPOT)
    {
        light_space = project_point(LIGHTS.spot_matrices[L.type_index], POSITION);        
        light_uv = light_space * 0.5 + 0.5;
    }
    if(L.type == LIGHT_SUN)
    {
        mat4 matrix = LIGHTS.sun_matrices[L.type_index*LIGHTS.cascades_count];
        matrix[3] = vec4(L.position, 1);
        light_space = project_point(matrix, POSITION);
        light_uv = light_space;
    }
    if(L.type == LIGHT_POINT)
    {
        light_space = POSITION - L.position;        
        light_uv = normalize(POSITION - L.position);
    }

    LightShaderInput I;
    I.L = L;
    I.LS = LS;
    I.light_space_position = light_space;
    I.light_uv = light_uv;

    LightShaderOutput O;
    O.color = LS.light_color;

    LIGHT_SHADER(I,O);
    
    RESULT = O.color;
}

#endif //PIXEL_SHADER

