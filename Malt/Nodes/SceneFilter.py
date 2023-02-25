from Malt.GL.GL import *
from Malt.GL.Texture import Texture
from Malt.GL.RenderTarget import RenderTarget
from Malt.PipelineNode import PipelineNode
from Malt.PipelineParameters import Parameter, Type
from copy import copy, deepcopy

class SceneFilter(PipelineNode):
    """
    Filters a Scene based on object tags.
    """

    def __init__(self, pipeline):
        PipelineNode.__init__(self, pipeline)
        self.last_scene = None
        self.matches = None
        self.non_matches = None
    
    @classmethod
    def reflect_inputs(cls):
        return {
            'Scene' : Parameter('Scene', Type.OTHER),
            'Filter' : Parameter('', Type.STRING)
        }
    
    @classmethod
    def reflect_outputs(cls):
        return {
            'Matches' : Parameter('Scene', Type.OTHER),
            'Non Matches' : Parameter('Scene', Type.OTHER)
        }
    
    def execute(self, parameters):
        inputs = parameters['IN']
        outputs = parameters['OUT']
        
        scene = inputs['Scene']
        tag = inputs['Filter']

        if scene != self.last_scene:
            self.last_scene = scene
            self.matches = copy(scene)
            self.matches.objects = []
            self.matches.shader_resources = copy(self.matches.shader_resources)
            self.non_matches = copy(scene)
            self.non_matches.objects = []
            self.non_matches.shader_resources = copy(self.non_matches.shader_resources)
            for obj in scene.objects:
                if tag in obj.tags:
                    self.matches.objects.append(obj)
                else:
                    self.non_matches.objects.append(obj)
            self.matches.batches = self.pipeline.build_scene_batches(self.matches.objects)
            self.non_matches.batches = self.pipeline.build_scene_batches(self.non_matches.objects)
            
        outputs['Matches'] = self.matches
        outputs['Non Matches'] = self.non_matches


NODE = SceneFilter
