# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy

class Camera(object):

    def __init__(self, camera_matrix, projection_matrix, parameters={}):
        self.camera_matrix = camera_matrix
        self.projection_matrix = projection_matrix
        self.parameters = parameters

class Material(object):

    def __init__(self, shader, parameters={}):
        self.shader = shader
        self.parameters = parameters

class Mesh(object):

    def __init__(self, mesh, parameters={}):
        self.mesh = mesh
        self.parameters = parameters

class Object(object):

    def __init__(self, matrix, mesh, material, parameters={}):
        self.matrix = matrix
        self.mesh = mesh
        self.material = material
        self.parameters = parameters
        self.negative_scale = False

class Light(object):

    def __init__(self):
        self.type = 0
        self.color = (0,0,0)
        self.parameters = {}
        self.position = (0,0,0)
        self.direction = (0,0,0)
        self.spot_angle = 0
        self.spot_blend = 0
        self.radius = 0
        self.matrix = None

class Scene(object):

    def __init__(self):
        self.camera = None
        self.objects = []
        self.lights = []
        self.parameters = {}
        self.world_parameters = {}
        self.frame = 0
        self.time = 0

