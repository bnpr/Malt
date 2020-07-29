# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

import math

#Rotated Grid Super Sampling pattern
def get_RGSS_samples(grid_size):
    samples = []
    for x in range(0, grid_size):
        for y in range(0, grid_size):
            _x = (x / grid_size) * 2.0 - 1.0 #(-1 ... +1 range)
            _y = (y / grid_size) * 2.0 - 1.0 #(-1 ... +1 range)

            angle = math.atan(1/2)
            sin = math.sin(angle)
            cos = math.cos(angle)
            r_x = _x * cos - _y * sin
            r_y = _x * sin + _y * cos
            
            scale = math.sqrt(5)/2
            r_x *= scale
            
            samples.append((r_x,r_y))
    
    #TODO: Reorder
    return samples
