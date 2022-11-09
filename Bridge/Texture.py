from Malt.GL import Texture
from Malt.GL.GL import *

TEXTURES = {}

def load_texture(msg):
    name = msg['name']
    data = msg['buffer'].buffer()
    resolution = msg['resolution']
    channels = msg['channels']
    sRGB = msg['sRGB']

    internal_formats = [
        GL_R32F,
        GL_RG32F,
        GL_RGB32F,
        GL_RGBA32F,
    ]
    pixel_formats = [
        GL_RED,
        GL_RG,
        GL_RGB,
        GL_RGBA
    ]
    internal_format = internal_formats[channels-1]
    pixel_format = pixel_formats[channels-1]
    
    if sRGB:
        if channels == 4:
            internal_format = GL_SRGB_ALPHA
        else:
            internal_format = GL_SRGB

    #Nearest + Anisotropy seems to yield the best results with temporal super sampling
    TEXTURES[name] = Texture.Texture(resolution, internal_format, GL_FLOAT, data, pixel_format=pixel_format, 
        wrap=GL_REPEAT, min_filter=GL_NEAREST_MIPMAP_NEAREST, build_mipmaps=True, anisotropy=True)

GRADIENTS = {}

def load_gradient(name, pixels, nearest):
    GRADIENTS[name] = Texture.Gradient(pixels, len(pixels)/4, nearest_interpolation=nearest)
