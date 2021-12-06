# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

import collections

import OpenGL
#OpenGL.ERROR_LOGGING = False
#OpenGL.FULL_LOGGING = False
#OpenGL.ERROR_ON_COPY = False
from OpenGL.GL import *
from OpenGL.extensions import hasGLExtension

if True: 
    #For some reason PyOpenGL doesnt support the most common depth/stencil buffer by default ???
    #https://sourceforge.net/p/pyopengl/bugs/223/
    from OpenGL import images
    images.TYPE_TO_ARRAYTYPE[ GL_UNSIGNED_INT_24_8 ] = GL_UNSIGNED_INT
    images.TIGHT_PACK_FORMATS[ GL_UNSIGNED_INT_24_8 ] = 4

NULL = None
GL_ENUMS = {}
GL_NAMES = {}

if True: #create new scope to import OpenGL
    from OpenGL import GL
    for e in dir(GL):
        if e.startswith('GL_'):
            GL_ENUMS[getattr(GL, e)] = e
            GL_NAMES[e] = getattr(GL, e)

class DrawQuery():

    def __init__(self):
        self.query = None
    
    def begin_query(self, query_type=GL_ANY_SAMPLES_PASSED):
        if self.query:
            glDeleteQueries(1, self.query)
        self.query = gl_buffer(GL_UNSIGNED_INT, 1)
        glGenQueries(1, self.query)
        glBeginQuery(query_type, self.query[0])

    def end_query(self):        
        glEndQuery(self.query_type)

    def begin_conditional_draw(self, wait_mode=GL_QUERY_WAIT):
        glBeginConditionalRender(self.query[0], wait_mode)
    
    def end_conditional_draw(self, wait_mode=GL_QUERY_WAIT):
        glEndConditionalRender()
    

def gl_buffer(type, size, data=None):
    types = {
        GL_BYTE : GLbyte,
        GL_UNSIGNED_BYTE : GLubyte,
        GL_SHORT : GLshort,
        GL_UNSIGNED_SHORT : GLushort,
        GL_INT : GLint,
        GL_UNSIGNED_INT : GLuint,
        GL_FLOAT : GLfloat,
        GL_DOUBLE : GLdouble,
        GL_BOOL : GLboolean,
    }
    gl_type = (types[type] * size)
    if data:
        try:
            return gl_type(*data)
        except:
            return gl_type(data)
    else:
        return gl_type()


def buffer_to_string(buffer):
    chars = []
    for char in list(buffer):
        if chr(char) == '\0':
            break
        chars.append(chr(char))
    return ''.join(chars)


