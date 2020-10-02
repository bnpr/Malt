# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from Malt import GL
from Malt import Mesh
from Malt import Parameter
from Malt import Pipeline
from Malt import PipelineTest
from Malt import RenderTarget
from Malt import Scene
from Malt import Shader
from Malt import Texture
from Malt import UBO
from Malt import Utils

from Malt.Render import AO
from Malt.Render import Common
from Malt.Render import DepthToCompositeDepth
from Malt.Render import Lighting
from Malt.Render import Line
from Malt.Render import Sampling

modules = [
    GL,
    Mesh,
    Parameter,
    Pipeline,
    PipelineTest,
    RenderTarget,
    Scene,
    Shader,
    Texture,
    UBO,
    Utils,
    AO,
    Common,
    DepthToCompositeDepth,
    Lighting,
    Line,
    Sampling,
]