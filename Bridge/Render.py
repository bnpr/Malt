import Malt
import Malt.Pipelines.NPR_Pipeline.NPR_Pipeline as NPR_Pipeline

from Malt.GL import GL
from Malt.GL.RenderTarget import RenderTarget
from Malt.GL.Texture import Texture

import Bridge.Mesh
import Bridge.Material

import ctypes

PIPELINE = None

def render(msg):
    global PIPELINE
    if PIPELINE is None:
        PIPELINE = NPR_Pipeline.NPR_Pipeline()

    scene = msg['scene']
    resolution = msg['resolution']
    viewport_id = msg['viewport_id']

    for mesh in scene.meshes:
        for i, submesh in enumerate(mesh):
           submesh.mesh = Bridge.Mesh.MESHES[submesh.mesh][i]
    
    for material in scene.materials:
        material.shader = Bridge.Material.get_shader(material.shader['path'], material.shader['parameters'])
    
    for obj in scene.objects:
        obj.matrix = (ctypes.c_float * 16)(*obj.matrix)
    
    scene.batches = PIPELINE.build_scene_batches(scene.objects)

    result = PIPELINE.render(resolution, scene, False, True)

    pixels = bytearray((resolution[0] * resolution[1] * 3))
    target = RenderTarget([result['COLOR']])
    target.bind()
    GL.glReadBuffer(GL.GL_COLOR_ATTACHMENT0)
    GL.glReadPixels(0, 0, resolution[0], resolution[1],
        GL.GL_RGB, GL. GL_UNSIGNED_BYTE, pixels)

    return pixels
    

