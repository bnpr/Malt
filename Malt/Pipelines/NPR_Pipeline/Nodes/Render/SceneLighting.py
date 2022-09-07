from Malt.GL.GL import *
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type

from Malt.Render import Common
from Malt.Render import Lighting
from Malt.Pipelines.NPR_Pipeline import NPR_Lighting

class SceneLighting(PipelineNode):
    """
    Renders the shadow maps and attaches them along the scene lights data to the *Scene* shader resources.
    """

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
        self.lights_buffer = Lighting.get_lights_buffer()
        self.light_groups_buffer = NPR_Lighting.NPR_LightsGroupsBuffer()
        self.shadowmaps_opaque = NPR_Lighting.NPR_ShadowMaps()
        self.shadowmaps_transparent = NPR_Lighting.NPR_TransparentShadowMaps()
        self.common_buffer = Common.CommonBuffer()

    @classmethod
    def reflect_inputs(cls):
        inputs = {}
        inputs['Scene'] = Parameter('Scene', Type.OTHER)
        inputs['Point Resolution'] = Parameter(2048, Type.INT, doc=
            "Shadowmap resolution for point lights *(for each cubemap side)*.")
        inputs['Point Resolution @ Preview'] = Parameter(512, Type.INT)
        
        inputs['Spot Resolution'] = Parameter(2048, Type.INT, doc=
            "Shadowmap resolution for spot lights.")
        inputs['Spot Resolution @ Preview'] = Parameter(512, Type.INT)
        
        inputs['Sun Resolution'] = Parameter(2048, Type.INT, doc=
            "Shadowmap resolution for sun light lights *(for each cascade side)*.")
        
        inputs['Sun Max Distance'] = Parameter(100, Type.FLOAT,doc="""
            The maximum distance from the view origin at which objects will still cast shadows.
            The lower the value, the higher the perceived resolution.""")
        inputs['Sun Max Distance @ Preview'] = Parameter(25, Type.FLOAT)
        
        inputs['Sun CSM Count'] = Parameter(4, Type.INT, doc=
            "The number of [Shadow Cascades](https://docs.microsoft.com/en-us/windows/win32/dxtecharts/cascaded-shadow-maps#cascaded-shadow-maps-and-perspective-aliasing) for sun lights.")
        inputs['Sun CSM Count @ Preview'] = Parameter(2, Type.INT)
        
        inputs['Sun CSM Distribution'] = Parameter(0.9, Type.FLOAT, doc="""
            Interpolates the cascades distribution along the view distance between linear distribution *(at 0)* and logarithmic distribution *(at 1)*.  
            The appropriate value depends on camera FOV and scene characteristics.""")
        return inputs
    
    @classmethod
    def reflect_outputs(cls):
        outputs = {}
        outputs['Scene'] = Parameter('Scene', Type.OTHER, doc=
            "The scene with the light data already loaded in the shader resources.")
        return outputs

    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']

        scene = inputs['Scene']
        if scene is None:
            return

        sample_offset = self.pipeline.get_sample(scene.world_parameters['Samples.Width'])
        opaque_batches, transparent_batches = self.pipeline.get_scene_batches(scene)

        inputs['Spot Resolution'] = max(8, inputs['Spot Resolution'])
        inputs['Sun Resolution'] = max(8, inputs['Sun Resolution'])
        inputs['Point Resolution'] = max(8, inputs['Point Resolution'])
        inputs['Sun CSM Count'] = max(1, inputs['Sun CSM Count'])

        self.lights_buffer.load(scene, 
            inputs['Spot Resolution'],
            inputs['Sun Resolution'],
            inputs['Point Resolution'],
            inputs['Sun CSM Count'], 
            inputs['Sun CSM Distribution'],
            inputs['Sun Max Distance'],
            sample_offset)
        self.light_groups_buffer.load(scene)
        self.shadowmaps_opaque.load(scene,
            inputs['Spot Resolution'],
            inputs['Sun Resolution'],
            inputs['Point Resolution'],
            inputs['Sun CSM Count'])
        self.shadowmaps_transparent.load(scene,
            inputs['Spot Resolution'],
            inputs['Sun Resolution'],
            inputs['Point Resolution'],
            inputs['Sun CSM Count'])
        
        shader_resources = scene.shader_resources.copy()
        shader_resources['COMMON_UNIFORMS'] = self.common_buffer
        shader_resources['SCENE_LIGHTS'] = self.lights_buffer

        def render_shadowmaps(lights, fbos_opaque, fbos_transparent):
            for light_index, light_matrices_pair in enumerate(lights.items()):
                light, matrices = light_matrices_pair
                for matrix_index, camera_projection_pair in enumerate(matrices): 
                    camera, projection = camera_projection_pair
                    i = light_index * len(matrices) + matrix_index
                    self.common_buffer.load(scene, fbos_opaque[i].resolution, (0,0), self.pipeline.sample_count, camera, projection)
                    def get_light_group_batches(batches):
                        result = {}
                        for material, meshes in batches.items():
                            if material and light.parameters['Light Group'] in material.parameters['Light Groups.Shadow']:
                                result[material] = meshes
                        return result
                    #TODO: Callback
                    self.pipeline.draw_scene_pass(fbos_opaque[i], get_light_group_batches(opaque_batches), 
                        'SHADOW_PASS', self.pipeline.default_shader['SHADOW_PASS'], shader_resources)
                    self.pipeline.draw_scene_pass(fbos_transparent[i], get_light_group_batches(transparent_batches), 
                        'SHADOW_PASS', self.pipeline.default_shader['SHADOW_PASS'], shader_resources)
        
        render_shadowmaps(self.lights_buffer.spots,
            self.shadowmaps_opaque.spot_fbos, self.shadowmaps_transparent.spot_fbos)
        
        glEnable(GL_DEPTH_CLAMP)
        render_shadowmaps(self.lights_buffer.suns,
            self.shadowmaps_opaque.sun_fbos, self.shadowmaps_transparent.sun_fbos)
        glDisable(GL_DEPTH_CLAMP)

        render_shadowmaps(self.lights_buffer.points,
            self.shadowmaps_opaque.point_fbos, self.shadowmaps_transparent.point_fbos)
        
        import copy
        scene = copy.copy(scene)
        scene.shader_resources = copy.copy(scene.shader_resources)

        scene.shader_resources['SCENE_LIGHTS'] = self.lights_buffer
        scene.shader_resources['LIGHT_GROUPS'] = self.light_groups_buffer
        scene.shader_resources['SHADOWMAPS'] = self.shadowmaps_opaque
        scene.shader_resources['TRANSPARENT_SHADOWMAPS'] = self.shadowmaps_transparent

        outputs['Scene'] = scene


NODE = SceneLighting

