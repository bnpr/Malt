#ifndef NODE_UTILS_VECTOR_GLSL
#define NODE_UTILS_VECTOR_GLSL

/*  META GLOBAL
    @meta: category=Vector;
*/

mat4 CONVERSION_TABLE[4*4] = mat4[4*4](
    mat4(1), MODEL, CAMERA*MODEL, PROJECTION*CAMERA*MODEL,
    inverse(MODEL), mat4(1), CAMERA, PROJECTION*CAMERA,
    inverse(CAMERA*MODEL), inverse(CAMERA), mat4(1), PROJECTION,
    inverse(PROJECTION*CAMERA*MODEL),inverse(PROJECTION*CAMERA),inverse(PROJECTION),mat4(1)
);

/*  META
    @Type: subtype=ENUM(Point,Vector,Normal);
    @From: subtype=ENUM(Object,World,Camera,Screen);
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
    mat4 m = CONVERSION_TABLE[clamp(From,0,3)*4 + clamp(To,0,3)];
    bool project = From == 3 || To == 3;
    if (project)
    {
        if(Type==0)//Point
        {
            Vector = project_point(m, Vector);
        }
        if(Type==1)//Vector
        {
            Vector = project_direction(m, POSITION, Vector);
        }
        if(Type==2)//Normal
        {
            Vector = project_normal(m, POSITION, Vector);
        }
    }
    else
    {
        if(Type==0)//Point
        {
            Vector = transform_point(m, Vector);
        }
        if(Type==1)//Vector
        {
            Vector = transform_direction(m, Vector);
        }
        if(Type==2)//Normal
        {
            Vector = transform_normal(m, Vector);
        }
    }
}

#endif // COMMON_VECTOR_GLSL
