#ifndef BAYER_GLSL
#define BAYER_GLSL

// Based on: https://en.wikipedia.org/wiki/Ordered_dithering

/* META GLOBAL
    @meta: internal=true;
*/

float bayer_mat2( int index ){
  int matrix[4] = int[4](
    0,2,
    3,1
  );
  return float( matrix[index]) / 4.0;
}

float bayer_mat3( int index ){
  int matrix[9] = int[9](
    0,7,3,
    6,5,2,
    4,1,8
  );
  return float( matrix[index]) / 9.0;
}

float bayer_mat4( int index ){
  int matrix[16] = int[16](
    0,8,2,10,
    12,4,14,6,
    3,11,1,9,
    15,7,13,5
  );
  return float( matrix[index]) / 16.0;
}

float bayer_mat8( int index ){
  int matrix[64] = int[64](
    0,32,8,40,2,34,10,42,
    48,16,56,24,50,18,58,26,
    12,44,4,36,14,46,6,38,
    60,28,53,20,62,30,54,22,
    3,35,11,43,1,33,9,41,
    51,19,59,27,49,17,57,25,
    15,47,7,39,13,45,5,37,
    63,31,55,23,61,29,53,21
  );
  return float( matrix[index]) / 64.0;
}

int bayer_index( vec2 uv, int size ){
  uv = floor( abs(vec2( 0 - uv.x, 1 - uv.y )) * vec2( float( size )));
  int index = int( uv.x ) + size * int( uv.y );
  return index;
}

#endif //BAYER_GLSL