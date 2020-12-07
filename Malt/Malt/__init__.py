# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from Malt import Scene
from Malt import Parameter
from Malt import Pipeline
from Malt import Utils

from Malt.GL import GL
from Malt.GL import Mesh
from Malt.GL import RenderTarget
from Malt.GL import Shader
from Malt.GL import Texture

from Malt.Pipelines.NPR_Pipeline import NPR_Lighting
from Malt.Pipelines.NPR_Pipeline import NPR_Pipeline

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
    RenderTarget,
    Scene,
    Shader,
    Texture,
    Utils,
    AO,
    NPR_Lighting,
    NPR_Pipeline,
    Common,
    DepthToCompositeDepth,
    Lighting,
    Line,
    Sampling,
]

