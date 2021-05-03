# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import ctypes
import numpy as np

from BlenderMalt import MaltPipeline

__TEXTURES = {}

def get_texture(texture):
    name = texture.name_full
    if name not in __TEXTURES or __TEXTURES[name] is None:
        __TEXTURES[name] = __load_texture(texture)
    return name

def __load_texture(texture):
    name = texture.name_full

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

    MaltPipeline.get_bridge().load_texture(name, (w,h), channels, sRGB)

    return True

__GRADIENTS = {}
__GRADIENT_RESOLUTION = 256

def get_gradient(color_ramp, material_name, name):
    full_name = material_name + '_' + name
    pixels = []
    
    if material_name not in __GRADIENTS:
        __GRADIENTS[material_name] = {}
    
    gradients = __GRADIENTS[material_name]
    
    if name not in gradients:
        for i in range(0, __GRADIENT_RESOLUTION):
            pixel = color_ramp.evaluate( i*(1.0 / __GRADIENT_RESOLUTION))
            pixels.extend(pixel)
        nearest = color_ramp.interpolation == 'CONSTANT'
        MaltPipeline.get_bridge().load_gradient(full_name, pixels, nearest)
        gradients[name] = full_name
    
    return full_name

def reset_textures():
    global __TEXTURES
    __TEXTURES = {}
    global __GRADIENTS
    __GRADIENTS = {}

def unload_texture(texture):
    __TEXTURES[texture.name_full] = None

def unload_gradients(material):
    __GRADIENTS[material.name_full] = {}

def register():
    pass

def unregister():
    pass
