GL_ENUMS = {}
GL_NAMES = {}

if True: #create new scope to import OpenGL
    from OpenGL import GL
    for e in dir(GL):
        if e.startswith('GL_'):
            GL_ENUMS[getattr(GL, e)] = e
            GL_NAMES[e] = getattr(GL, e)

from OpenGL.GL import *

def print_format_prop(format, prop):
    read = glGetInternalformativ(GL_TEXTURE_2D, format, prop, 1)
    print(GL_ENUMS[format], GL_ENUMS[prop], GL_ENUMS[read])

def print_format_props(format):
    print_format_prop(format, GL_READ_PIXELS)
    print_format_prop(format, GL_READ_PIXELS_FORMAT)
    print_format_prop(format, GL_READ_PIXELS_TYPE)
    print_format_prop(format, GL_TEXTURE_IMAGE_FORMAT)
    print_format_prop(format, GL_TEXTURE_IMAGE_TYPE)

print_format_props(GL_RGB8)
print_format_props(GL_RGBA8)
print_format_props(GL_RGB16F)
print_format_props(GL_RGBA16F)
print_format_props(GL_RGB32F)
print_format_props(GL_RGBA32F)
