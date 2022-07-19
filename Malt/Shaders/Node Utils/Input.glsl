#ifndef NODE_UTILS_INPUT_GLSL
#define NODE_UTILS_INPUT_GLSL

/* META GLOBAL
    @meta: category=Input;
*/

void Geometry(
    out vec3 Position,
    out vec3 Normal,
    out vec3 True_Normal,
    out vec3 Incoming,
    out bool Is_Backfacing,
    out uvec4 Id
)
{
    Position = POSITION;
    Normal = NORMAL;
    True_Normal = true_normal();
    Incoming = -view_direction();
    Is_Backfacing = !is_front_facing();
    Id = ID;
}

/*  META
    @Index: min=0; max=3;
    @uv: label=UV;
*/
void UV_Map(
    int Index,
    out vec2 uv
)
{
    uv = UV[Index];
}

/*  META
    @meta: subcategory=Tangent; label=UV Map;
    @UV_Index: min=0; max=3;
*/
void Tangent_UV_Map(
    int UV_Index,
    out vec3 Tangent,
    out vec3 Bitangent
)
{
    Tangent = get_tangent(UV_Index);
    Bitangent = get_bitangent(UV_Index);
}
/*  META
    @meta: subcategory=Tangent; label=Radial;
    @axis: subtype=ENUM(X,Y,Z); default=2;
*/
void Tangent_Radial(
    int axis,
    out vec3 Tangent,
    out vec3 Bitangent
)
{
    vec3 _axis = vec3[3](vec3(1,0,0), vec3(0,1,0), vec3(0,0,1))[axis];
    Tangent = radial_tangent(NORMAL, _axis);
    Bitangent = normalize(cross(NORMAL, Tangent)) * (is_front_facing() ? 1 : -1);
}
/*  META
    @meta: subcategory=Tangent; label=Procedural UV;
*/
void Tangent_Procedural_UV(
    vec2 UV,
    out vec3 Tangent,
    out vec3 Bitangent
)
{
    vec4 t = compute_tangent(UV);
    Tangent = t.xyz;
    Bitangent = normalize(cross(NORMAL, Tangent)) * t.w;
}

/* META
    @Normal: default=NORMAL; subtype=Vector;
*/
void Fresnel(
    vec3 Normal,
    out float Facing,
    out float Fresnel
)
{
    Facing = dot(Normal, -view_direction());
    Fresnel = abs(1.0 - Facing);
}

/*  META
    @Index: min=0; max=3;
    @uv: label=UV;
*/
void Vertex_Color(
    int Index,
    out vec4 Vertex_Color
)
{
    Vertex_Color = COLOR[Index];
}

void Object_Info(
    out vec3 Position,
    out uint Id,
    out vec4 Random
)
{
    Position = model_position();
    Id = ID.x;
    Random = hash(Id);
}

void Render_Info(
    out vec2 Resolution,
    out int Current_Sample,
    out vec2 Sample_Offset
)
{
    Resolution = RESOLUTION;
    Current_Sample = SAMPLE_COUNT;
    Sample_Offset = SAMPLE_OFFSET;
}

void Time_Info(
    out float Time,
    out int Frame
)
{
    Time = TIME;
    Frame = FRAME;
}

#endif //NODE_UTILS_INPUT_GLSL
