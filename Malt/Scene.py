class Camera():

    def __init__(self, camera_matrix, projection_matrix, parameters={}):
        self.camera_matrix = camera_matrix
        self.projection_matrix = projection_matrix
        self.parameters = parameters

class Material():

    def __init__(self, shader, parameters={}):
        self.shader = shader
        self.parameters = parameters

class Mesh():

    def __init__(self, mesh, parameters={}):
        self.mesh = mesh
        self.parameters = parameters

class Object():

    def __init__(self, matrix, mesh, material, parameters={}, mirror_scale=False):
        self.matrix = matrix
        self.mesh = mesh
        self.material = material
        self.parameters = parameters
        self.mirror_scale = mirror_scale

class Light():

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

class Scene():

    def __init__(self):
        self.camera = None
        self.objects = []
        self.lights = []
        self.parameters = {}
        self.world_parameters = {}
        self.frame = 0
        self.time = 0

        self.batches = None
        self.shader_resources = {}

class ShaderResource():
    
    def shader_callback(self, shader):
        pass

class TextureShaderResource():

    def __init__(self, name, texture):
        self.name = name
        self.texture = texture
    
    def shader_callback(self, shader):
        if self.name in shader.textures.keys():
            shader.textures[self.name] = self.texture

        

