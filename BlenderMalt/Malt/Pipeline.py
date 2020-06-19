# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from .Mesh import Mesh
from .Shader import Shader

class PipelineParameters(object):

    def __init__(self):
        self.world = {}
        self.camera = {}
        self.object = {}
        self.mesh = {}
        self.material = {}
        self.light = {}
        self.sun_light = {}
        self.spot_light = {}
        self.spot_light = {}


class Pipeline(object):

    def __init__(self):
        self.parameters = PipelineParameters()
        self.shaders = {}

    def get_parameters(self):
        return self.parameters
    
    def compile_shader(self, shader_path):
        return {
            'uniforms':{}, 
            'error':None,
        }
    
    def load_mesh(self, position, index, normal=None, uvs={}, colors={}):
        return Mesh(position,index,normal,uvs,colors)

    def render(self, resolution, scene):
        #return texture
        pass

