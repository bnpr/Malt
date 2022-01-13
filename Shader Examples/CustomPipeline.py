from Malt.Pipelines.NPR_Pipeline.NPR_Pipeline import *

from Malt.Utils import LOG

class Extended_NPR_Pipeline(NPR_Pipeline):

    def __init__(self):
        super().__init__()
        self.parameters.world['Custom Post Process'] = MaterialParameter('', '.screen.glsl')
    
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
                LOG.error(traceback.format_exc)
        
        return result

PIPELINE = Extended_NPR_Pipeline
