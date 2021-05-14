# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import ctypes
import numpy as np
from . import MaltPipeline

__TEXTURES = {}

def get_texture(texture):
    name = texture.name_full
    if name not in __TEXTURES or __TEXTURES[name] is None:
        __TEXTURES[name] = __load_texture(texture)
    return name

def __load_texture(texture):
    # https://numpy.org/doc/stable/reference/arrays.interface.html
    class ArrayInterface(object):
        def __init__(self, typestr, length, address):
            self.__array_interface__={
                'shape':(length,),
                'data':(address, False),
                'typestr':typestr,
                'version':3,
            }

    w,h = texture.size
    channels = int(texture.channels)
    size = w*h*channels
    sRGB = texture.colorspace_settings.name == 'sRGB'
    if size == 0:
        return True

    buffer = MaltPipeline.get_bridge().get_texture_buffer(size)
    array_interface = ArrayInterface('<f4', size, ctypes.addressof(buffer))
    #np_view = np.empty(size, dtype=np.float32)
    np_view = np.array(array_interface, copy=False)
    texture.pixels.foreach_get(np_view)
    
    MaltPipeline.get_bridge().load_texture(texture.name_full, (w,h), channels, sRGB)

__GRADIENTS = {}
__GRADIENT_RESOLUTION = 256

def get_gradient(texture):
    name = texture.name_full
    if name not in __GRADIENTS:
        __GRADIENTS[name] = __load_gradient(texture)
    return __GRADIENTS[name]

def __load_gradient(texture):
    pixels = []
    for i in range(0, __GRADIENT_RESOLUTION):
        pixel = texture.color_ramp.evaluate( i*(1.0 / __GRADIENT_RESOLUTION))
        pixels.extend(pixel)
    nearest = texture.color_ramp.interpolation == 'CONSTANT'
    MaltPipeline.get_bridge().load_gradient(texture.name_full, pixels, nearest)
    
def reset_textures():
    global __TEXTURES
    __TEXTURES = {}
    global __GRADIENTS
    __GRADIENTS = {}

def unload_texture(texture):
    __TEXTURES[texture.name_full] = None

def unload_gradients(texture):
    __GRADIENTS[texture.name_full] = {}

def register():
    pass

def unregister():
    pass
