# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from .GL import *

class Parameter(object):
    def __init__(self, type, array_length=1, value=None, getters={'BLENDER':None}):
        self.type = type
        self.base_type, self.base_size = uniform_type_to_base_type_and_size(type)
        self.array_length = array_length
        self.value = value
        self.getters = getters

  