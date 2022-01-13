#ifdef _WIN32
#define EXPORT extern "C" __declspec( dllexport )
#else
#define EXPORT extern "C" __attribute__ ((visibility ("default")))
#endif

//Blender Data Structures

struct BVert
{
    float co[3];
    short no[3];
    char flag, bweight;
};

struct BLoop
{
    unsigned int v;
    unsigned int e;
};

struct BLoopTri
{
    unsigned int tri[3];
    unsigned int poly;
};

struct BLoopUV
{
    float uv[2];
    int flag;
};

struct BPoly {
  int loopstart;
  int totloop;
  short mat_nr;
  char flag, _pad;
};

// BPoly flag
enum {
  ME_SMOOTH = (1 << 0),
  ME_FACE_SEL = (1 << 1),
};

EXPORT void retrieve_mesh_data(void* in_verts, void* in_loops, int loop_count, void* in_loop_tris, int loop_tri_count, void* in_polys,
                        float* out_positions, short* out_normals, unsigned int** out_indices, unsigned int* out_index_lengths)
{
    BVert* verts = (BVert*)in_verts;
    BLoop* loops = (BLoop*)in_loops;
    BLoopTri* loop_tris = (BLoopTri*)in_loop_tris;
    BPoly* polys = (BPoly*)in_polys;

    int p = 0, n = 0;

    for(int i = 0; i < loop_count; i++)
    {
        out_positions[p++] = verts[loops[i].v].co[0];
        out_positions[p++] = verts[loops[i].v].co[1];
        out_positions[p++] = verts[loops[i].v].co[2];

        out_normals[n++] = verts[loops[i].v].no[0];
        out_normals[n++] = verts[loops[i].v].no[1];
        out_normals[n++] = verts[loops[i].v].no[2];
    }

    unsigned int* mat_i = out_index_lengths;

    for(int i = 0; i < loop_tri_count; i++)
    {
        short mat = polys[loop_tris[i].poly].mat_nr;
        out_indices[mat][mat_i[mat]++] = loop_tris[i].tri[0];
        out_indices[mat][mat_i[mat]++] = loop_tris[i].tri[1];
        out_indices[mat][mat_i[mat]++] = loop_tris[i].tri[2];
    }
}

EXPORT void retrieve_mesh_uv(void* in_uvs, int loop_count, float* out_uvs)
{
    BLoopUV* uvs = (BLoopUV*)in_uvs;

    int uv = 0;

    for(int i = 0; i < loop_count; i++)
    {
        out_uvs[uv++] = uvs[i].uv[0];
        out_uvs[uv++] = uvs[i].uv[1];
    }
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
    BPoly* polys = (BPoly*)in_polys;

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

