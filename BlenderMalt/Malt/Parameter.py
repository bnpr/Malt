# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from .GL import *

from enum import Enum

class Type(Enum):
    BOOL=0
    INT=1
    FLOAT=2
    STRING=3
    ENUM=5
    TEXTURE=6
    GRADIENT=7
    SHADER=8
    RENDER_TARGET=9

class Parameter(object):
    def __init__(self, value, type, size=1, getters={'BLENDER':None}):
        self.value = value
        self.type = type
        self.size = size
        self.getters = getters

    @classmethod
    def from_uniform(cls, uniform):
        type, size = gl_type_to_malt_type(uniform.type)
        
        return Parameter(uniform.value, type, size)


def gl_type_to_malt_type(gl_type):
    types = {
        'FLOAT' : Type.FLOAT,
        'DOUBLE' : Type.FLOAT,
        'INT' : Type.INT,
        'BOOL' : Type.BOOL,
        'SAMPLER' : Type.TEXTURE,
    }
    sizes = {
        'VEC2' : 2,
        'VEC3' : 3,
        'VEC4' : 4,
        'MAT2' : 4,
        'MAT3' : 9,
        'MAT4' : 16,
    }
    gl_name = GL_ENUMS[gl_type]

    for type_name, type in types.items():
        if type_name in gl_name:
            for size_name, size in sizes.items():
                if size_name in gl_name:
                    return (type, size)
            return (type, 1)
    
    raise Exception(gl_name, ' Uniform type not supported')

  