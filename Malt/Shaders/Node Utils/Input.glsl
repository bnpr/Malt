#ifndef NODE_UTILS_INPUT_GLSL
#define NODE_UTILS_INPUT_GLSL

/* META GLOBAL
    @meta: category=Input;
*/

void geometry(
    int uv_index,
    out vec3 position,
    out vec3 normal,
    out vec3 tangent,
    out vec3 bitangent,
    out vec3 incoming,
    out vec3 out_true_normal,
    out float facing,
    out bool front_facing
    ) {
        position = POSITION;
        normal = NORMAL;
        tangent = get_tangent(uv_index);
        bitangent = get_bitangent(uv_index);
        incoming = get_incoming(camera_position(), position);
        out_true_normal = true_normal();
        facing = dot(normal, incoming);
        front_facing = is_front_facing();
}

vec4 vertex_color( int index ){
    return COLOR[index];
}

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

void id(
    out uvec4 id,
    out uvec4 original_id
    ) {
        id = ID;
        original_id = IO_ID;
    }

int _get_fps(){ return int(round(FRAME / TIME));}

void time(
    out int frame,
    out float time,
    out int fps
    ) {
        frame = FRAME;
        time = TIME;
        fps = _get_fps();
    }

void render(
    out vec2 render_resolution,
    out vec2 sample_offset,
    out int sample_count,
    out float out_pixel_depth,
    out float out_pixel_world_size
    ) {
        render_resolution = vec2(RESOLUTION);
        sample_offset = SAMPLE_OFFSET;
        sample_count = SAMPLE_COUNT;
        out_pixel_depth = pixel_depth();
        out_pixel_world_size = pixel_world_size();
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