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

EXPORT float* mesh_tangents_ptr(void* in_mesh)
{
	Mesh* mesh = (Mesh*)in_mesh;
	float* ptr = (float*)CustomData_get_layer(&mesh->corner_data, CD_MLOOPTANGENT);
    
  return ptr;
}
