# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from .Mesh import Mesh
from .Shader import Shader

class PipelineParameters(object):

    def __init__(self, scene={}, world={}, camera={}, object={}, material={}, light={}):
        self.scene = scene
        self.world = world
        self.camera = camera
        self.object = object
        self.material = material
        self.light = light
        

class Pipeline(object):

    def __init__(self):
        self.parameters = PipelineParameters()

    def get_parameters(self):
        return self.parameters
    
    def compile_shader(self, shader_path):
        return {
            'uniforms':{}, 
            'error':None,
        }

    def render(self, resolution, scene):
        #return texture
        pass

