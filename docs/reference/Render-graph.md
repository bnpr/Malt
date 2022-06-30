# Render Graph Reference
---
### **LineRender**
Expands the line up to the width especified in the *Line Width* texture
and composites it on top of the *Color* texture.

- **Inputs**  
	- **Color** *: ( Texture )*  
	- **Line Color** *: ( Texture )*  
	- **Line Width** *: ( Texture )*  
	- **Max Width** *: ( Int ) - default = 10*  
	>The maximum width the shader can render.
	Increasing the value lowers the render performance.
	- **Line Scale** *: ( Float ) - default = 1.0*  
	>Scale all Line Width values with this one.  
	*(Useful for rendering at different resolutions)*
	- **Normal Depth** *: ( Texture )*  
	- **ID** *: ( Texture )*  
- **Outputs**  
	- **Color** *: ( Texture )*  
---
### **SuperSamplingAA**
Performs anti-aliasing by accumulating multiple render samples into a single texture.

- **Inputs**  
	- **Color** *: ( Texture )*  
- **Outputs**  
	- **Color** *: ( Texture )*  
---
### **RenderLayers**
>Graph Type / Pass : *Render Layer / Render Layer*

Renders the scene geometry, using multiple *depth peeling* layers for transparent objects.  
The node sockets are dynamic, based on the graph selected.

- **Inputs**  
	- **Scene** *: ( Scene )*  
	- **Transparent Layers** *: ( Int ) - default = 4*  
	>The maximum number of overlapping transparency layers.  
	Incresing this values lowers performance.
---
### **SceneLighting**
Renders the shadow maps and attaches them along the scene lights data to the *Scene* shader resources.

- **Inputs**  
	- **Scene** *: ( Scene )*  
	- **Point Resolution** *: ( Int ) - default = 2048*  
	>Shadowmap resolution for point lights *(for each cubemap side)*.
	- **Spot Resolution** *: ( Int ) - default = 2048*  
	>Shadowmap resolution for spot lights.
	- **Sun Resolution** *: ( Int ) - default = 2048*  
	>Shadowmap resolution for sun light lights *(for each cascade side)*.
	- **Sun Max Distance** *: ( Float ) - default = 100*  
	>The maximum distance from the view origin at which objects will still cast shadows.
	The lower the value, the higher the perceived resolution.
	- **Sun CSM Count** *: ( Int ) - default = 4*  
	>The number of [Shadow Cascades](https://docs.microsoft.com/en-us/windows/win32/dxtecharts/cascaded-shadow-maps#cascaded-shadow-maps-and-perspective-aliasing) for sun lights.
	- **Sun CSM Distribution** *: ( Float ) - default = 0.9*  
	>Interpolates the cascades distribution along the view distance between linear distribution *(at 0)* and logarithmic distribution *(at 1)*.  
	The appropriate value depends on camera FOV and scene characteristics.
- **Outputs**  
	- **Scene** *: ( Scene )*  
---
### **ScreenPass**
>Graph Type / Pass : *Screen / SCREEN_SHADER*

Renders a full screen shader pass.  
The node sockets are dynamic, based on the shader selected.

