#include "Common.glsl"
#include "Lighting/Lighting.glsl"

#ifdef VERTEX_SHADER
void main()
{
    POSITION = in_position;
    UV[0] = in_position.xy * 0.5 + 0.5;

    VERTEX_SETUP_OUTPUT();

    gl_Position = vec4(POSITION, 1);
}
#endif
