# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from Malt.GL import *

class PipelineParameters(object):

    def __init__(self, scene={}, world={}, camera={}, object={}, material={}, mesh={}, light={}):
        self.scene = scene
        self.world = world
        self.camera = camera
        self.object = object
        self.material = material
        self.mesh = mesh
        self.light = light

from enum import Enum

class Type(object):
    BOOL=0
    INT=1
    FLOAT=2
    STRING=3
    ENUM=5
    TEXTURE=6
    GRADIENT=7
    MATERIAL=8
    RENDER_TARGET=9

class Parameter(object):
    def __init__(self, default_value, type, size=1):
        self.default_value = default_value
        self.type = type
        self.size = size

    @classmethod
    def from_uniform(cls, uniform):
        type, size = gl_type_to_malt_type(uniform.type)
        value = uniform.value
        if type in (Type.INT, Type.FLOAT, Type.BOOL):
            if size > 1:
                value = tuple(value)
            else:
                value = value[0]
        #TODO: uniform length ??? (Arrays)
        return Parameter(value, type, size)

def gl_type_to_malt_type(gl_type):
    types = {
        'FLOAT' : Type.FLOAT,
        'DOUBLE' : Type.FLOAT,
        'INT' : Type.INT,
        'BOOL' : Type.BOOL,
        'SAMPLER_1D' : Type.GRADIENT,
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

  