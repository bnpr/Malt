# NPR Pipeline

The [*NPR Pipeline*](NPR_Pipeline.py) is the main *Malt Pipeline*.  
It's designed for stylized and NPR rendering and aside from common features like supersampling, lighting and shadow maps it suports:

* Line Rendering.
* Object ID rendering for NPR features like disabling self-shadows.
* Transparent Shadow Maps.
* User defined custom Light Shaders.
* Order independent transparency (implemented via [*Depth Peeling*](https://en.wikipedia.org/wiki/Depth_peeling)).

## Pipeline Shaders

The *NPR Pipeline* supports 3 types of shaders:

| Type | Source | Extension | Description |
|------|-------------|-----------|-------------|
| **Mesh** | [NPR_MeshShader.glsl](../../Shaders/Pipelines/NPR_Pipeline/NPR_MeshShader.glsl) | *.mesh.gsl* | Material shaders for rendering objects.
| **Light** | [NPR_LightShader.glsl](../../Shaders/Pipelines/NPR_Pipeline/NPR_LightShader.glsl) | *.light.gsl* | Custom light shader that outputs the light color and intensity at a certain point.
| **Screen** | [NPR_ScreenShader.glsl](../../Shaders/Pipelines/NPR_Pipeline/NPR_ScreenShader.glsl) | *.screen.gsl* | Shaders for screen-space effects, like post-processing.

There are examples for each shader type in the [Shader Examples](../../../Shader%20Examples) folder.


## Render overview

The high level overview of how the *NPR Pipeline* renders a frame sample is:

* Load *Scene* data.
* Render ShadowMaps (*SHADOW_PASS*).
* Composite opaque and transparent (depth peeling) layers. For each layer:
    * Render a *PRE_PASS* that outputs the World Space Normal, Pixel Depth and Object IDs.
    * Render custom *Light Shaders* results to screen-space textures.
    * Render the *MAIN_PASS* that outputs the *final color* and the data needed for *line rendering*.
    * Expand and composite the *final line result* on top of the *final color*.
* Composite the result on top of the results from previous samples.


## Extending the Pipeline

The simplest way to extend the *NPR Pipeline* is by inheriting the class and overriding the *draw_layer* function.

```python

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

        shader = scene.world_parameters['Custom Post Process']
        if shader and shader['SHADER']:
            # Pass any input needed to the shader (must be declared in the shader source)
            shader['SHADER'].textures['IN_COLOR'] = result
            self.draw_screen_pass(shader['SHADER'], self.fbo_postpro)

            return self.t_postpro
        
        return result

```

