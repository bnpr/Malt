# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

import ctypes
from . import MaltPipeline

__TEXTURES = {}

def get_texture(texture):
    name = texture.name_full
    if name not in __TEXTURES or __TEXTURES[name] is None:
        __TEXTURES[name] = __load_texture(texture)
    return __TEXTURES[name]


def __load_texture(texture):
    w,h = texture.size
    channels = int(texture.channels)
    size = w*h*channels
    sRGB = False
    if size == 0:
        return True

    buffer = MaltPipeline.get_bridge().get_shared_buffer(ctypes.c_float, size)
    texture.pixels.foreach_get(buffer.as_np_array())
    
    MaltPipeline.get_bridge().load_texture(texture.name_full, buffer, (w,h), channels, sRGB)
    
    from Bridge.Proxys import TextureProxy
    return TextureProxy(texture.name_full)

__GRADIENTS = {}
__GRADIENT_RESOLUTION = 256
# Blender doesn't trigger depsgraph updates for newly created textures,
# so we always reload gradients until it's been succesfully unloaded once (TODO)
__GRADIENTS_WORKAROUND = []
def add_gradient_workaround(texture):
    __GRADIENTS_WORKAROUND.append(texture.name_full)

def get_gradient(texture):
    name = texture.name_full
    if name not in __GRADIENTS or __GRADIENTS[name] is None or name in __GRADIENTS_WORKAROUND:
        __GRADIENTS[name] = __load_gradient(texture)
    return __GRADIENTS[name]

def __load_gradient(texture):
    pixels = []
    for i in range(0, __GRADIENT_RESOLUTION):
        pixel = texture.color_ramp.evaluate( i*(1.0 / __GRADIENT_RESOLUTION))
        pixels.extend(pixel)
    nearest = texture.color_ramp.interpolation == 'CONSTANT'
    MaltPipeline.get_bridge().load_gradient(texture.name_full, pixels, nearest)
    from Bridge.Proxys import GradientProxy
    return GradientProxy(texture.name_full)

def copy_color_ramp(old, new):
    new.color_mode = old.color_mode
    new.hue_interpolation = old.hue_interpolation
    new.interpolation = old.interpolation
    while len(new.elements) > len(old.elements):
        new.elements.remove(new.elements[len(new.elements)-1])
    for i, o in enumerate(old.elements):
        n = new.elements[i] if i < len(new.elements) else new.elements.new(o.position) 
        n.position = o.position
        n.color = o.color[:]
        n.alpha = o.alpha
    
def reset_textures():
    global __TEXTURES
    __TEXTURES = {}
    global __GRADIENTS
    __GRADIENTS = {}

def unload_texture(texture):
    __TEXTURES[texture.name_full] = None

def unload_gradients(texture):
    __GRADIENTS[texture.name_full] = None
    if texture.name_full in __GRADIENTS_WORKAROUND:
        __GRADIENTS_WORKAROUND.remove(texture.name_full)

def register():
    pass

def unregister():
    pass
