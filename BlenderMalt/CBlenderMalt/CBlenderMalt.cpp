#include "stdio.h"
#include "string.h"

#ifdef _WIN32
#define EXPORT extern "C" __declspec( dllexport )
#else
#define EXPORT extern "C" __attribute__ ((visibility ("default")))
#endif

#include "blender_dna/DNA_mesh_types.h"
#include "blender_dna/DNA_meshdata_types.h"

//blenkernel/intern/customdata.cc

int CustomData_get_active_layer_index(const CustomData *data, int type)
{
	const int layer_index = data->typemap[type];
	//BLI_assert(customdata_typemap_is_valid(data));
	return (layer_index != -1) ? layer_index + data->layers[layer_index].active : -1;
}

void *CustomData_get_layer(const CustomData *data, int type)
{
	/* get the layer index of the active layer of type */
	int layer_index = CustomData_get_active_layer_index(data, type);
	if (layer_index == -1) {
	return nullptr;
	}

	return data->layers[layer_index].data;
}

int CustomData_get_layer_index(const CustomData *data, int type)
{
	//BLI_assert(customdata_typemap_is_valid(data));
	return data->typemap[type];
}

int CustomData_get_layer_index_n(const struct CustomData *data, int type, int n)
{
	//BLI_assert(n >= 0);
	int i = CustomData_get_layer_index(data, type);

	if (i != -1) {
		//BLI_assert(i + n < data->totlayer);
		i = (data->layers[i + n].type == type) ? (i + n) : (-1);
	}

	return i;
}

#define STREQ(a, b) (strcmp(a, b) == 0)

int CustomData_get_named_layer_index(const CustomData *data, const int type, const char *name)
{
  for (int i = 0; i < data->totlayer; i++) {
    if (data->layers[i].type == type) {
      if (STREQ(data->layers[i].name, name)) {
        return i;
      }
    }
  }

  return -1;
}

void *CustomData_get_layer_named(const CustomData *data, const int type, const char *name)
{
  int layer_index = CustomData_get_named_layer_index(data, type, name);
  if (layer_index == -1) {
    return nullptr;
  }

  return data->layers[layer_index].data;
}

void *CustomData_get_layer_n(const CustomData *data, int type, int n)
{
	/* get the layer index of the active layer of type */
	int layer_index = CustomData_get_layer_index_n(data, type, n);
	if (layer_index == -1) {
		return nullptr;
	}

	return data->layers[layer_index].data;
}

// CBlenderMalt API

EXPORT void retrieve_mesh_data(void* in_mesh, void* in_verts, void* in_loops, void* in_polys,
    void* in_loop_tris, int loop_tri_count,
    float* out_positions, float* out_normals, unsigned int** out_indices, unsigned int* out_index_lengths)
{
	Mesh* mesh = (Mesh*)in_mesh;
    MVert* verts = (MVert*)in_verts;
    MLoop* loops = (MLoop*)in_loops;
    MPoly* polys = (MPoly*)in_polys;
    MLoopTri* loop_tris = (MLoopTri*)in_loop_tris;

	float* normals = (float*)CustomData_get_layer(&mesh->ldata, CD_NORMAL);
    int* mat_indices = (int*)CustomData_get_layer_named(&mesh->pdata, CD_PROP_INT32, "material_index");
    
    if(normals)
    {
        memcpy(out_normals, normals, mesh->totloop * sizeof(float) * 3);
    }

    int p = 0, n = 0;

    for(int i = 0; i < mesh->totloop; i++)
    {
        out_positions[p++] = verts[loops[i].v].co[0];
        out_positions[p++] = verts[loops[i].v].co[1];
        out_positions[p++] = verts[loops[i].v].co[2];
    }

    unsigned int* mat_i = out_index_lengths;

    for(int i = 0; i < loop_tri_count; i++)
    {
        int mat = mat_indices ? mat_indices[loop_tris[i].poly] : 0;
        out_indices[mat][mat_i[mat]++] = loop_tris[i].tri[0];
        out_indices[mat][mat_i[mat]++] = loop_tris[i].tri[1];
        out_indices[mat][mat_i[mat]++] = loop_tris[i].tri[2];
    }
}

EXPORT void retrieve_mesh_uv(void* in_uvs, int loop_count, float* out_uvs)
{
    MLoopUV* uvs = (MLoopUV*)in_uvs;

    int uv = 0;

    for(int i = 0; i < loop_count; i++)
    {
        out_uvs[uv++] = uvs[i].uv[0];
        out_uvs[uv++] = uvs[i].uv[1];
    }
}

EXPORT float* mesh_tangents_ptr(void* in_mesh)
{
	Mesh* mesh = (Mesh*)in_mesh;
	float* ptr = (float*)CustomData_get_layer(&mesh->ldata, CD_MLOOPTANGENT);
    
    return ptr;
}

EXPORT void pack_tangents(float* in_tangents, float* in_bitangent_signs, int loop_count, float* out_tangents)
{
    for(int i = 0; i < loop_count; i++)
    {
        out_tangents[i*4+0] = in_tangents[i*3+0];
        out_tangents[i*4+1] = in_tangents[i*3+1];
        out_tangents[i*4+2] = in_tangents[i*3+2];
        out_tangents[i*4+3] = in_bitangent_signs[i];
    }
}

EXPORT bool has_flat_polys(void* in_polys, int polys_count)
{
    MPoly* polys = (MPoly*)in_polys;

    bool has_flat_poly = false;

    for(int i = 0; i < polys_count; i++)
    {
        has_flat_poly |= (polys[i].flag & ME_SMOOTH) == 0;
    }

    return has_flat_poly;
}

struct RenderPass {
	struct RenderPass *next, *prev;
	int channels;
	char name[64];
	char chan_id[8];
	float *rect;
	int rectx, recty;

	char fullname[64];
	char view[64];
	int view_id;

	int pad;
};

EXPORT float* get_rect_ptr(void* render_pass_ptr)
{
    return ((RenderPass*)render_pass_ptr)->rect;
}
