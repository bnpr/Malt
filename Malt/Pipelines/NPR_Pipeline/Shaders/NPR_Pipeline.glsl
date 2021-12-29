//Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

//Every NPR_Pipeline shader should include this file regardless of its type.
//IS_MESH_SHADER and the likes are defined by the pipeline itself based on the shader file extension.

#ifndef NPR_PIPELINE

#define NPR_PIPELINE

#include "NPR_Pipeline/NPR_Intellisense.glsl"

#ifdef IS_MESH_SHADER
#include "NPR_Pipeline/NPR_MeshShader.glsl"
#endif

#ifdef IS_LIGHT_SHADER
#include "NPR_Pipeline/NPR_LightShader.glsl"
#endif

#ifdef IS_SCREEN_SHADER
#include "NPR_Pipeline/NPR_ScreenShader.glsl"
#endif

#endif

