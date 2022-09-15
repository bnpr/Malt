#ifndef NODE_UTILS_2_VECTOR_GLSL
#define NODE_UTILS_2_VECTOR_GLSL

/*  META GLOBAL
    @meta: category=Vector;
*/

mat4 TRANSFORM_CONVERSION_TABLE[3*3] = mat4[3*3](
    mat4(1), MODEL, CAMERA*MODEL,
    inverse(MODEL), mat4(1), CAMERA,
    inverse(CAMERA*MODEL), inverse(CAMERA), mat4(1)
);

/*  META
    @Type: subtype=ENUM(Point,Vector,Normal);
    @From: subtype=ENUM(Object,World,Camera);
    @To: subtype=ENUM(Object,World,Camera,Screen);
    @Vector: subtype=Vector;
*/
void Transform(
    int Type,
    int From,
    int To,
    inout vec3 Vector
)
{
    mat4 m = TRANSFORM_CONVERSION_TABLE[clamp(From,0,2)*3 + clamp(To,0,2)];
    bool project = To == 3;
    if(Type==0)//Point
    {
        if(project)
        {
            m = PROJECTION * m;
            Vector = project_point_to_screen_coordinates(m, Vector);
        }
        else
        {
            Vector = transform_point(m, Vector);
        }
    }
    else
    {
        if(Type==1)//Vector
        {
            Vector = transform_direction(m, Vector);
        }
        if(Type==2)//Normal
        {
            Vector = transform_normal(m, Vector);
        }
        if (project)
        {
            Vector = camera_direction_to_screen_space(Vector);
        }
    }
}

/* META
    @meta: subcategory=Mapping; label=Point;
    @vector: subtype=Vector; default='vec3(0.0)';
    @location: subtype=Vector;
    @rotation: subtype=Euler;
    @scale: subtype=Vector; default=vec3(1.0);
*/
vec3 mapping_point(vec3 vector, vec3 location, vec3 rotation, vec3 scale)
{
    vec3 result = vector * scale;
    result = transform_point(mat4_rotation_from_euler(rotation), result);
    return result + location;
}

/* META
    @meta: subcategory=Mapping; label=Texture;
    @vector: subtype=Vector; default='vec3(0.0)';
    @location: subtype=Vector;
    @rotation: subtype=Euler;
    @scale: subtype=Vector; default=vec3(1.0);
*/
vec3 mapping_texture(vec3 vector, vec3 location, vec3 rotation, vec3 scale)
{
    vec3 result = vector - location;
    result = transform_point(inverse(mat4_rotation_from_euler(rotation)), result);
    return result / scale;
}

/* META
    @meta: subcategory=Mapping; label=Vector;
    @vector: subtype=Vector; default='vec3(0.0)';
    @rotation: subtype=Euler;
    @scale: subtype=Vector; default=vec3(1.0);
*/
vec3 mapping_vector(vec3 vector, vec3 rotation, vec3 scale)
{
    return transform_direction(mat4_rotation_from_euler(rotation), vector * scale);
}

/* META
    @meta: subcategory=Mapping; label=Normal;
    @vector: subtype=Vector; default='vec3(0.0)';
    @rotation: subtype=Euler;
    @scale: subtype=Vector; default=vec3(1.0);
*/

vec3 mapping_normal(vec3 vector, vec3 rotation, vec3 scale)
{
    return normalize(mapping_vector(vector, rotation, scale));
}

#endif // COMMON_VECTOR_GLSL
