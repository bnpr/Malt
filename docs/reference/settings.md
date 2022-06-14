# Malt Settings
## World
- **Material**
	- **Default** *: ( Material )** = Malt - Default Mesh Material*  
	>The default material, used for objects with no material assigned.
	- **Override** *: ( Material )** = None*  
	>When set, overrides all scene materials with this one.
- **Viewport**
	- **Resolution Scale** *: ( Float )** = 1.0*  
	>A multiplier for the viewport resolution.
It can be lowered to improve viewport performance or for specific styles, like *pixel art*.
	- **Smooth Interpolation** *: ( Bool )** = True*  
	>The interpolation mode used when *Resolution Scale* is not 1.
Toggles between *Nearest/Bilinear* interpolation.
- **Samples**
	- **Grid Size** *: ( Int )** = 8*  
	>The number of render samples per side in the sampling grid. 
The total number of samples is the square of this value minus the samples that fall outside the sampling radius.  
Higher values will provide cleaner renders at the cost of increased render times.
	- **Width** *: ( Float )** = 1.0*  
	>The width (and height) of the sampling grid. 
Larger values will result in smoother/blurrier images while lower values will result in sharper/more aliased ones. 
Keep it withing the 1-2 range for best results.
- **Render** *: ( Graph )** = Default Render*  
>The *Render Node Tree* used to render the scene. 
See [Render & Render Layers](#Render & Render Layers) for more info.
## Material
- **Light Groups**
	- **Light** *: ( Int )** = [1, 0, 0, 0]*  
	>The *Light Groups* (up to 4) that lit this material.
	- **Shadow** *: ( Int )** = [1, 0, 0, 0]*  
	>The *Light Groups* (up to 4) that this material casts shadows on.
## Mesh
- **double_sided** *: ( Bool )** = False*  
>Disables backface culling, so geometry is rendered from both sides.
- **precomputed_tangents** *: ( Bool )** = False*  
>Load precomputed mesh tangents *(needed for improving normal mapping quality on low poly meshes)*. 
It's disabled by default since it slows down mesh loading in Blender.  
When disabled, the *tangents* are calculated on the fly from the *pixel shader*.
## Light
- **Light Group** *: ( Int )** = 1*  
>Lights only affect materials with a matching *Light Group* value.
- **Shader** *: ( Material )** = None*  
>When set, the *Material* with a custom *Light Shader* or *Light Node Tree* that will be used to render this light.
