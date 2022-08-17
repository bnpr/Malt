#define NO_NORMAL_INPUT
#define NO_UV_INPUT
#define NO_VERTEX_COLOR_INPUT
#define NO_MODEL_INPUT
#define NO_ID_INPUT

#include "NPR_Intellisense.glsl"
#include "Common.glsl"
#include "Lighting/Lighting.glsl"

uniform int LIGHT_INDEX;

#ifdef VERTEX_SHADER
void main()
{
    DEFAULT_SCREEN_VERTEX_SHADER();
}
#endif

#ifdef PIXEL_SHADER

uniform sampler2D IN_DEPTH;

layout (location = 0) out vec3 RESULT;

void LIGHT_SHADER(vec3 relative_coordinates, vec3 uvw, inout vec3 color, inout float attenuation);

void main()
{
    PIXEL_SETUP_INPUT();

    float depth = texelFetch(IN_DEPTH, screen_pixel(), 0).x;
    POSITION = screen_to_camera(screen_uv(), depth);
    POSITION = transform_point(inverse(CAMERA), POSITION);

    Light L = LIGHTS.lights[LIGHT_INDEX];
    LitSurface LS = lit_surface(POSITION, vec3(0), L, false);
    
    vec3 light_space = vec3(0);
    vec3 uvw = vec3(0);

    if(L.type == LIGHT_SPOT)
    {
        light_space = project_point(LIGHTS.spot_matrices[L.type_index], POSITION);
        uvw.xy = light_space.xy * 0.5 + 0.5;
    }
    if(L.type == LIGHT_SUN)
    {
        vec3 z = L.direction;
        vec3 c = vec3(0,0,1);
        if(abs(dot(z, c)) < 1.0)
        {
            vec3 x = normalize(cross(c, z));
            vec3 y = normalize(cross(x, z));
            mat3 rotation = mat3(x,y,z);
            mat4 m = mat4_translation(L.position) * mat4(rotation);
            m = inverse(m);

            light_space = transform_point(m, POSITION);
        }
        else
        {
            light_space = POSITION;
            light_space -= L.position;
        }
        
        uvw.xy = light_space.xy;
    }
    if(L.type == LIGHT_POINT)
    {
        light_space = POSITION - L.position;
        light_space /= L.radius;    
        
        uvw = normalize(light_space);
    }

    vec3 color = L.color;
    float attenuation = LS.P;

    LIGHT_SHADER(light_space, uvw, color, attenuation);
    
    RESULT = color * attenuation;
}

#endif //PIXEL_SHADER

