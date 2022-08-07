#ifndef NODE_UTILS_INPUT_GLSL
#define NODE_UTILS_INPUT_GLSL

/*  META GLOBAL
    @meta: category=Input;
*/

/*  META
    @Coordinate_Space: label=Space; subtype=ENUM(Object,World,Camera,Screen); default=1;
    @Normal: default=NORMAL;
    @IOR: label=IOR; min=1.0; max=3.0; default=1.45;
*/
void Geometry(
    int Coordinate_Space,
    out vec3 Position,
    out vec3 Incoming,
    out vec3 Normal,
    out vec3 True_Normal,
    out bool Is_Backfacing,
    out float Facing,
    out float Fresnel,
    out vec3 Reflection,
    out vec3 Refraction,
    float IOR
)
{
    Position = POSITION;
    Incoming = -view_direction();
    Normal = NORMAL;
    True_Normal = true_normal();
    Facing = dot(Normal, Incoming);
    Is_Backfacing = !is_front_facing();
    float F0 = pow((1-IOR) / (1+IOR), 2);
    Fresnel = F_cook_torrance(Facing, F0);
    Reflection = reflect(view_direction(), Normal);
    Refraction = refract(Incoming, Normal, 1.0 / IOR);

    if(Coordinate_Space == 0) //Object
    {
        mat4 m = inverse(MODEL);
        Position = transform_point(m, Position);
        Incoming = transform_normal(m, Incoming);
        Normal = transform_normal(m, Normal);
        True_Normal = transform_normal(m, True_Normal);
        Reflection = transform_normal(m, Reflection);
        Refraction = transform_normal(m, Refraction);
    }
    if(Coordinate_Space == 2) //Camera
    {
        mat4 m = CAMERA;
        Position = transform_point(m, Position);
        Incoming = transform_normal(m, Incoming);
        Normal = transform_normal(m, Normal);
        True_Normal = transform_normal(m, True_Normal);
        Reflection = transform_normal(m, Reflection);
        Refraction = transform_normal(m, Refraction);
    }
    if(Coordinate_Space == 3) //Screen
    {
        mat4 m = PROJECTION * CAMERA;
        Position = project_point_to_screen_coordinates(m, Position);
        Incoming = project_normal(m, POSITION, Incoming);
        Normal = project_normal(m, POSITION, Normal);
        True_Normal = project_normal(m, POSITION, True_Normal);
        Reflection = project_normal(m, POSITION, Reflection);
        Refraction = project_normal(m, POSITION, Refraction);
    }
}

/*  META
    @meta: label=UV Map;
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
    @Axis: subtype=ENUM(X,Y,Z); default=2;
    @Object_Space: default=true;
*/
void Tangent_Radial(
    int Axis,
    bool Object_Space,
    out vec3 Tangent,
    out vec3 Bitangent
)
{
    vec3 normal = NORMAL;
    if(Object_Space)
    {
        normal = transform_normal(inverse(MODEL), normal);
    }
    vec3 _axis = vec3[3](vec3(1,0,0), vec3(0,1,0), vec3(0,0,1))[Axis];
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

/*  META
    @meta: label=Id;
*/
void ID_Node(
    out vec4 Object_Id,
    out vec4 Custom_Id_A,
    out vec4 Custom_Id_B,
    out vec4 Custom_Id_C
)
{
    Object_Id = unpackUnorm4x8(IO_ID.x);
    Custom_Id_A = unpackUnorm4x8(IO_ID.y);
    Custom_Id_B = unpackUnorm4x8(IO_ID.z);
    Custom_Id_C = unpackUnorm4x8(IO_ID.w);
}

void Object_Info(
    out vec3 Position,
    out mat4 Rotation,
    out vec3 Scale,
    out vec4 Id,
    out mat4 Matrix
)
{
    Position = MODEL[3].xyz;
    vec3 i = MODEL[0].xyz;
    vec3 j = MODEL[1].xyz;
    vec3 k = MODEL[2].xyz;
    //TODO: Signed Scale?
    Scale = vec3(length(i), length(j), length(k));
    i /= Scale.x;
    j /= Scale.y;
    k /= Scale.z;
    Rotation = mat4(mat3(i,j,k));

    Id = unpackUnorm4x8(IO_ID.x);
    Matrix = MODEL;
}

/*  META
    @Screen_UV: label=Screen UV;
*/
void Camera_Data(
    out vec3 View_Direction,
    out vec2 Screen_UV,
    out float Z_Depth,
    out float View_Distance,
    out vec3 Camera_Position,
    out mat4 Camera_Matrix,
    out mat4 Projection_Matrix,
    out bool Is_Orthographic
)
{
    Screen_UV = screen_uv();
    View_Direction = view_direction();
    Z_Depth = -transform_point(CAMERA, POSITION).z;
    View_Distance = distance(Camera_Position, POSITION);
    Camera_Position = camera_position();
    Camera_Matrix = CAMERA;
    Projection_Matrix = PROJECTION;
    Is_Orthographic = is_ortho(PROJECTION);
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

void Random(
    float seed,
    out vec4 per_object,
    out vec4 per_sample,
    out vec4 per_pixel
)
{
    per_object = random_per_object(seed);
    per_sample = random_per_sample(seed);
    per_pixel = random_per_pixel(seed);
}

/* META
    @uv: default=UV[0];
    @normal: default=NORMAL;
    @tangent: default=get_tangent(0);
    @incoming: default=-view_direction();
*/
void Curve_View_Mapping(
    out vec2 Uv,
    out float Facing
)
{
    Uv = curve_view_mapping(UV[0], NORMAL, get_tangent(0), -view_direction());
    Facing = 1 - (abs(Uv.y - 0.5) * 2);
}

#endif //NODE_UTILS_INPUT_GLSL
