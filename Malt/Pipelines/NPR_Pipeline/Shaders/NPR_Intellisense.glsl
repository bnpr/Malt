//This is just for getting text editor autocompletion on user shaders.
//It doesn't have any effect at runtime
#ifdef __INTELLISENSE__

#define VERTEX_SHADER
#define PIXEL_SHADER

#define IS_MESH_SHADER

#define CUSTOM_VERTEX_DISPLACEMENT
#define SHADOW_PASS
#define PRE_PASS
#define MAIN_PASS

#define IS_LIGHT_SHADER

#define IS_SCREEN_SHADER

#endif //__INTELLISENSE__
