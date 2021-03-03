#Copyright (c) 2020 BlenderNPR and contributors. MIT license.

from Malt.Pipelines.NPR_Pipeline.NPR_Pipeline import NPR_Pipeline
from Malt.Parameter import *
from Malt.GL.GL import *
from Malt.GL.RenderTarget import RenderTarget
from Malt.GL.Texture import Texture

import logging as log

class Extended_NPR_Pipeline(NPR_Pipeline):

    def __init__(self):
        super().__init__()
        self.parameters.world['Custom Post Process'] = MaterialParameter('', 'screen')
    
    def setup_render_targets(self, resolution):
        super().setup_render_targets(resolution)
        
        self.t_postpro = Texture(resolution, GL_RGBA32F)
        self.fbo_postpro = RenderTarget([self.t_postpro])
    
    def draw_layer(self, batches, scene, background_color=(0,0,0,0)):
        result = super().draw_layer(batches, scene, background_color)

        material = scene.world_parameters['Custom Post Process']
        if material and material.shader:
            try:
                shader = material.shader['SHADER']
                # Pass any input needed to the shader (must be declared in the shader source)
                shader.textures['IN_COLOR'] = result
                shader.textures['IN_ID'] = self.t_prepass_id
                self.draw_screen_pass(shader, self.fbo_postpro)
                return self.t_postpro
            except:
                import traceback
                log.error(traceback.format_exc)
        
        return result

PIPELINE = Extended_NPR_Pipeline
