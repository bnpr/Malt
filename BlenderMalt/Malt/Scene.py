# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy

class Camera(object):

    def __init__(self, camera_matrix, projection_matrix, parameters={}):
        self.camera_matrix = camera_matrix
        self.projection_matrix = projection_matrix

class Material(object):

    def __init__(self, shader, parameters={}):
        self.shader = shader
        self.parameters = parameters

class Object(object):

    def __init__(self, matrix, mesh, material, parameters={}):
        self.matrix = matrix
        self.mesh = mesh
        self.material = material

class SunLight(object):

    def __init__(self, direction, color=(1,1,1), parameters={}):
        self.direction = direction
        self.color = color

class SpotLight(object):

    def __init__(self, position, direction, radius, color=(1,1,1), parameters={}):
        self.position = position
        self.direction = direction
        self.radius = radius
        self.color = color
        
class PointLight(object):

    def __init__(self, position, radius, color=(1,1,1), parameters={}):
        self.position = position
        self.radius = radius
        self.color = color     

class Scene(object):

    def __init__(self):
        self.camera = None
        self.objects = []
        self.sun_lights = []
        self.spot_lights = []
        self.point_lights = []
