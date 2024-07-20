#include "stdio.h"
#include "mikktspace.h"

#ifdef _WIN32
#define EXPORT extern "C" __declspec( dllexport )
#else
#define EXPORT extern "C" __attribute__ ((visibility ("default")))
#endif

EXPORT void retrieve_mesh_data(
  float* in_positions,
  int* in_loop_verts, int loop_count,
  int* in_loop_tris,
  int* in_loop_tri_polys, int loop_tri_count,
  int* in_mat_indices,
  float* out_positions, unsigned int** out_indices, unsigned int* out_index_lengths)
{
  for(int i = 0; i < loop_count; i++)
  {
    out_positions[i*3+0] = in_positions[in_loop_verts[i]*3+0];
    out_positions[i*3+1] = in_positions[in_loop_verts[i]*3+1];
    out_positions[i*3+2] = in_positions[in_loop_verts[i]*3+2];
  }

  unsigned int* mat_i = out_index_lengths;

  for(int i = 0; i < loop_tri_count; i++)
  {
    int mat = in_mat_indices ? in_mat_indices[in_loop_tri_polys[i]] : 0;
    out_indices[mat][mat_i[mat]++] = in_loop_tris[i*3+0];
    out_indices[mat][mat_i[mat]++] = in_loop_tris[i*3+1];
    out_indices[mat][mat_i[mat]++] = in_loop_tris[i*3+2];
  }
}

EXPORT bool mesh_tangents(
  int* in_indices, int index_len,
  float* in_positions, float* in_normals, float* in_uvs,
  float* out_tangents)
{
  struct MData
  {
    int* indices;
    int index_len;
    float* positions;
    float* normals;
    float* uvs;
    float* tangents;
  };

  MData data = {
    in_indices,
    index_len,
    in_positions,
    in_normals,
    in_uvs,
    out_tangents,
  };

  SMikkTSpaceInterface mti = {0};
  mti.m_getNumFaces = [](const SMikkTSpaceContext * pContext){
    return ((MData*)pContext->m_pUserData)->index_len / 3;
  };

	mti.m_getNumVerticesOfFace = [](const SMikkTSpaceContext * pContext, const int iFace){
    return 3;
  };

	mti.m_getPosition = [](const SMikkTSpaceContext * pContext, float fvPosOut[], const int iFace, const int iVert){
    MData* m = (MData*)pContext->m_pUserData;
    int i = iFace * 3 + iVert;
    fvPosOut[0] = m->positions[m->indices[i] * 3 + 0];
    fvPosOut[1] = m->positions[m->indices[i] * 3 + 1];
    fvPosOut[2] = m->positions[m->indices[i] * 3 + 2];
  };

	mti.m_getNormal = [](const SMikkTSpaceContext * pContext, float fvNormOut[], const int iFace, const int iVert){
    MData* m = (MData*)pContext->m_pUserData;
    int i = iFace * 3 + iVert;
    fvNormOut[0] = m->normals[m->indices[i] * 3 + 0];
    fvNormOut[1] = m->normals[m->indices[i] * 3 + 1];
    fvNormOut[2] = m->normals[m->indices[i] * 3 + 2];
  };

	mti.m_getTexCoord = [](const SMikkTSpaceContext * pContext, float fvTexcOut[], const int iFace, const int iVert){
    MData* m = (MData*)pContext->m_pUserData;
    int i = iFace * 3 + iVert;
    fvTexcOut[0] = m->uvs[m->indices[i] * 2 + 0];
    fvTexcOut[1] = m->uvs[m->indices[i] * 2 + 1];
  };

	mti.m_setTSpaceBasic = [](const SMikkTSpaceContext * pContext, const float fvTangent[], const float fSign, const int iFace, const int iVert){
    MData* m = (MData*)pContext->m_pUserData;
    int i = iFace * 3 + iVert;
    m->tangents[m->indices[i] * 4 + 0] = fvTangent[0];
    m->tangents[m->indices[i] * 4 + 1] = fvTangent[1];
    m->tangents[m->indices[i] * 4 + 2] = fvTangent[2];
    m->tangents[m->indices[i] * 4 + 3] = fSign;
  };
  
  SMikkTSpaceContext mtc;
  mtc.m_pInterface = &mti;
  mtc.m_pUserData = &data;

  return genTangSpaceDefault(&mtc);
}
