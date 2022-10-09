import ctypes

from Malt.GL.Shader import UBO

class C_CommonBuffer(ctypes.Structure):
    _fields_ = [
        ('CAMERA', ctypes.c_float*16),
        ('PROJECTION', ctypes.c_float*16),
        ('RESOLUTION', ctypes.c_int*2),
        ('SAMPLE_OFFSET', ctypes.c_float*2),
        ('SAMPLE_COUNT', ctypes.c_int),
        ('FRAME', ctypes.c_int),
        ('TIME', ctypes.c_float),
        ('__padding', ctypes.c_int),
    ]

def bake_sample_offset(projection_matrix, sample_offset, resolution):
    offset_x = sample_offset[0] / resolution[0]
    offset_y = sample_offset[1] / resolution[1]
    if projection_matrix[-1] == 1.0:
        #Orthographic camera
        projection_matrix[12] += offset_x
        projection_matrix[13] += offset_y
    else:
        #Perspective camera
        projection_matrix[8] += offset_x
        projection_matrix[9] += offset_y

class CommonBuffer():
    
    def __init__(self):
        self.data = C_CommonBuffer()
        self.UBO = UBO()
    
    def load(self, scene, resolution, sample_offset=(0,0), sample_count=0, camera=None, projection = None):
        self.data.CAMERA = tuple(camera if camera else scene.camera.camera_matrix)
        self.data.PROJECTION = tuple(projection if projection else scene.camera.projection_matrix)
        self.data.RESOLUTION = resolution
        self.data.SAMPLE_OFFSET = sample_offset
        self.data.SAMPLE_COUNT = sample_count
        self.data.FRAME = scene.frame
        self.data.TIME = scene.time
        
        bake_sample_offset(self.data.PROJECTION, sample_offset, resolution)

        self.UBO.load_data(self.data)
    
    def bind(self, block):
        self.UBO.bind(block)
    
    def shader_callback(self, shader):
        if 'COMMON_UNIFORMS' in shader.uniform_blocks:
            self.bind(shader.uniform_blocks['COMMON_UNIFORMS'])
