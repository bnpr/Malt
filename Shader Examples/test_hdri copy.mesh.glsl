
uniform sampler2D environment_texture;

uniform float sample_theta = PI / 8.0;

vec4 sample_environment_texture(vec3 v)
{
    vec2 uv = vec2(atan(v.y, v.x), asin(v.z));
    vec2 inverse_atan = vec2(0.1591, 0.3183);
    uv *= inverse_atan;
    uv += 0.5;
    return texelFetch(environment_texture, ivec2(uv * textureSize(environment_texture, 0)), 0);
    return texture(environment_texture, uv);
}

@MAIN_PASS_PIXEL_SHADER
{
    // Generate a random TBN matrix
    vec3 random_vec = random_vector(random_per_pixel, 0).xyz;
    random_vec.xyz = random_vec.xyz * 2.0 - 1.0;

    Light light = LIGHTS.lights[0];
    LitSurface surface = lit_surface(POSITION, normalize(NORMAL), light);

    vec3 normal = -reflect(surface.V, surface.N);
    vec3 tangent = normalize(random_vec - normal * dot(random_vec, normal));
    vec3 bitangent = cross(normal, tangent);
    mat3 TBN = mat3(tangent, bitangent, normal);

    float theta = get_random(0) * sample_theta;

    vec3 local_normal = vec3(sin(theta), 0, cos(theta));

    OUT_COLOR.rgb = sample_environment_texture(normalize(TBN * local_normal)).rgb;
    OUT_COLOR.rgb = min(OUT_COLOR.rgb, vec3(2));
    OUT_COLOR.a = 1.0;
}

