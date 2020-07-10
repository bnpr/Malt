# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from . import GL
from . import Mesh
from . import Parameter
from . import Pipeline
from . import PipelineTest
from . import RenderTarget
from . import Scene
from . import Shader
from . import Texture
from . import UBO

from .Render import Common
from .Render import Lighting

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
    Common,
    Lighting,
]