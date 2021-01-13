//Copyright (c) 2020 BlenderNPR and contributors. MIT license.

//Every NPR_Pipeline shader should include this file regardless of its type.
//IS_MESH_SHADER and the likes are defined by the pipeline itself based on the shader file extension.

#ifdef IS_MESH_SHADER
#include "NPR_Pipeline/NPR_MeshShader.glsl"
#endif

#ifdef IS_LIGHT_SHADER
#include "NPR_Pipeline/NPR_LightShader.glsl"
#endif

#ifdef IS_SCREEN_SHADER
#include "NPR_Pipeline/NPR_ScreenShader.glsl"
#endif

//This is a hacky way to get text editor autocompletion on user shaders.
//It doesn't have any effect while rendering
#ifdef __INTELLISENSE__

#define VERTEX_SHADER
#define PIXEL_SHADER
#define SHADOW_PASS
#define PRE_PASS
#define MAIN_PASS

#include "NPR_Pipeline/NPR_MeshShader.glsl"
#include "NPR_Pipeline/NPR_LightShader.glsl"
#include "NPR_Pipeline/NPR_ScreenShader.glsl"

#endif

