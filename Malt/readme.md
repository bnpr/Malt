# Malt

## Introduction

*Malt* is a fully customizable rendering framework written in **Python** and **OpenGL**.

Its main goal is to support offline rendering for **animation** and **illustration**, with special care put into supporting the needs of **stylized, non photo-realistic rendering** and being **accesible** to technical artists and users without previous graphics programming experience.

Therefore, while it's a **real-time renderer**, it **prioritizes image quality, flexibility and simplicity over rendering performance**.

## Malt Pipelines

The core class in *Malt* is the [*Pipeline*](Pipeline.py).
*Malt* allows to write completely custom render *Pipelines* while providing ready to use render utilities in the [*Shaders*](Shaders) and [*Render*](Render) libraries.

*Malt* is meant to be used by a *Host* application, like [*BlenderMalt*](../BlenderMalt).  
The *Host* is responsible for preparing and sending the *Scene* data to *Malt*, including already loaded and ready to use [*Meshes*, *Shaders* and *Textures*](GL). 

### Render

*Pipelines* main task is to implement a *render* function.
The *render* function takes a *Scene* and must return the rendered result as a *Texture*.

### Scene

The [*Scene*](Scene.py) class makes as little assumptions as posible about the data needed by the *Pipeline*.  
Instead, the *Pipeline* can declare custom [*Parameters*](PipelineParameters.py) for each *Scene* object type.  
The host is responsible for exposing those parameters so users can edit them.

### Materials

Additionaly, Pipelines are responsible for compiling *Materials*.  
A *Material* is a *Python Dictionary* of [Shaders](GL/Shader.py) with an arbitrary number of entries.  
The host is responsible for sending back scene objects with their respective materials and the shader parameters already setup.  

*Materials* should share the same source code for all the *Shaders* they generate by using conditional compilation through the *Preprocesor*.  
By default *Pipelines* declares the *VERTEX_SHADER* define when generating the *Vertex Shader* source code and *PIXEL_SHADER* for *Pixel/Fragment Shaders*.

### Implementing a Pipeline

Custom *Pipelines* can be implemented by creating a new *class* that inherits the *Pipeline* *class*. The pipeline can then be loaded from the *Host* settings.

The main functions to override are:

* *\_\_init__*: *Pipeline Parameters* *(self.parameters)* should be registered here, in addition to any *Render Resource* like *Shaders* and *UBOs* needed by the *Pipeline*.

> 💡 Since there can be multiple instances of the same *Pipeline*, it's a good practice to share resources between them when possible, to shorten *Pipeline* creation times and lower memory consumption.

* *setup_render_targets*: Any resolution dependent resource, like *RenderTargets* should be created here. This function is called whenever the *Pipeline* resolution changes, including the first time *render* is called.  

* *compile_material_from_source*: This should return a dictionary of all the *Shaders* generated from a *Pipeline* *Material*.

* *do_render*: This one is called by the *render* function after setup and as its name implies should render a whole frame and return it as a *Texture*.

#### Minimal example

```Python
class MiniPipeline(Pipeline):

    DEFAULT_SHADER = None

    def __init__(self):
        super().__init__()

        self.parameters.world['Background Color'] = Parameter((0.5,0.5,0.5,1), Type.FLOAT, 4)

        self.common_buffer = Common.CommonBuffer()
        
        if MiniPipeline.DEFAULT_SHADER is None: 
            source = '''
            #include "Common.glsl"

            #ifdef VERTEX_SHADER
            void main()
            {
                DEFAULT_VERTEX_SHADER();
            }
            #endif

            #ifdef PIXEL_SHADER
            layout (location = 0) out vec4 RESULT;
            void main()
            {
                RESULT = vec4(1);
            }
            #endif
            '''
            MiniPipeline.DEFAULT_SHADER = self.compile_material_from_source('mesh', source)
        
        self.default_shader = MiniPipeline.DEFAULT_SHADER
        
    def compile_material_from_source(self, material_type, source, include_paths=[]):
        return {
            'MAIN_PASS' : self.compile_shader_from_source(
                source, include_paths, ['MAIN_PASS']
            )
        }
    
    def setup_render_targets(self, resolution):
        self.t_depth = Texture(resolution, GL_DEPTH_COMPONENT32F)
        self.t_main_color = Texture(resolution, GL_RGBA32F)
        self.fbo_main = RenderTarget([self.t_main_color], self.t_depth)
        
    def do_render(self, resolution, scene, is_final_render, is_new_frame):
        self.common_buffer.load(scene, resolution)
        
        UBOS = { 'COMMON_UNIFORMS' : self.common_buffer }

        self.fbo_main.clear([scene.world_parameters['Background Color']], 1)

        self.draw_scene_pass(self.fbo_main, scene.batches, 'MAIN_PASS', self.default_shader['MAIN_PASS'], UBOS)

        return { 'COLOR' : self.t_main_color }
```

For a complete example see the [NPR_Pipeline](Pipelines/NPR_Pipeline)

