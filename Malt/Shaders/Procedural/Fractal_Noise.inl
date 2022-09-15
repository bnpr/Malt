//Should define TILE
//Should declare coord and tile_size (if TILE)

vec4 color = vec4(0);
float weight = 1.0;
float total_weight = 0.0;
detail_balance = clamp(detail_balance, 0.00001, 1.0);
detail = max(1.0, detail);

for (int i = 0; i < ceil(detail); i++) 
{
    #if TILE != 0
        vec4 noise = noise(coord, tile_size);
    #else
        vec4 noise = noise(coord);
    #endif
    float octave_weight = (i + 1 > floor(detail))? mod(detail, 1.0) : 1.0;
    weight *= detail_balance * 2 * octave_weight;
    color += weight * noise;
    total_weight += weight;
    coord *= 2.0;
    #if TILE != 0
        tile_size *= 2;
    #endif
}

color /= total_weight;