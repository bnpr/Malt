#ifndef NODE_UTILS_INPUT_GLSL
#define NODE_UTILS_INPUT_GLSL

/* META GLOBAL
    @meta: category=Input;
    @out_true_normal: label=True Normal;
*/

void geometry(
    out vec3 position,
    out vec3 normal,
    out vec3 incoming,
    out vec3 True_Normal,
    out bool front_facing
    ) {
        position = POSITION;
        normal = NORMAL;
        incoming = get_incoming(camera_position(), position);
        True_Normal = true_normal();
        front_facing = is_front_facing();
}

/* META
    @position: default=POSITION; subtype=Vector;
    @normal: default=NORMAL; subtype=Vector;
*/
void layer_weight(
    vec3 position,
    vec3 normal,
    out float facing,
    out float fresnel
    ) {
        facing = dot( normal, get_incoming(camera_position(), position));
        fresnel = 0.5; // WIP
    }

/* META @index: min=0; max=3; */
vec4 vertex_color( int index ){
    return COLOR[index];
}

/* META 
    @meta: label=UV Map;
    @index: min=0; max=3;
*/
vec2 uv_map( int index ){
    return UV[index];
}

void object_info(
    out vec3 location,
    out mat4 object_matrix,
    out float object_distance,
    out vec4 random
    ) {
        location = (MODEL * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
        object_matrix = MODEL;
        object_distance = distance((CAMERA * vec4( 0.0, 0.0, 0.0, 1.0)).xyz, location);
        random = hash(unpackUnorm4x8(IO_ID.x).xy);
    } 
/* META @meta: label=ID; */
void id(
    out uvec4 id,
    out uvec4 original_id
    ) {
        id = ID;
        original_id = IO_ID;
    }

void time(
    out int frame,
    out float time
    ) {
        frame = FRAME;
        time = TIME;
    }

void render(
    out vec2 render_resolution,
    out vec2 sample_offset,
    out int sample_count,
    out float Pixel_Depth,
    out float Pixel_World_Size
    ) {
        render_resolution = vec2(RESOLUTION);
        sample_offset = SAMPLE_OFFSET;
        sample_count = SAMPLE_COUNT;
        Pixel_Depth = pixel_depth();
        Pixel_World_Size = pixel_world_size();
    }

void camera(
    out vec3 location,
    out vec3 direction,
    out vec2 window,
    out mat4 camera_matrix,
    out mat4 projection_matrix
    ) {
        location = camera_position();
        direction = view_direction();
        window = screen_uv();
        camera_matrix = CAMERA;
        projection_matrix = PROJECTION;
    }

#endif // NODE_UTILS_INPUT_GLSL