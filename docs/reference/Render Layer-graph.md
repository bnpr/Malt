# Render Layer Graph Reference
---
## Render
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
### **MainPass**
>Graph Type / Pass : *Mesh / MAIN_PASS_PIXEL_SHADER*

Renders the scene geometry using the *Mesh Main Pass*.  
The node sockets are dynamic, based on the *Main Pass Custom IO*.  
If *Normal Depth/ID* is empty, the *Pre Pass* *Normal Depth/ID* will be used.

- **Inputs**  
	- **Scene** *: ( Scene )*  
	- **Normal Depth** *: ( Texture )*  
	- **ID** *: ( Texture )*  
---
### **PrePass**
>Graph Type / Pass : *Mesh / PRE_PASS_PIXEL_SHADER*

Renders the scene geometry using the *Mesh Pre Pass*.  
The node sockets are dynamic, based on the *Pre Pass Custom IO*.  
If *Normal Depth/ID* is empty, the *PrePass* *Normal Depth/ID* will be used.

- **Inputs**  
	- **Scene** *: ( Scene )*  
- **Outputs**  
	- **Scene** *: ( Scene )*  
	- **Normal Depth** *: ( Texture )*  
	- **ID** *: ( Texture )*  
---
### **ScreenPass**
>Graph Type / Pass : *Screen / SCREEN_SHADER*

Renders a full screen shader pass.  
The node sockets are dynamic, based on the shader selected.  
If *Normal Depth/ID* is empty, the *PrePass* *Normal Depth/ID* will be used.

- **Inputs**  
	- **Layer Only** *: ( Bool ) - default = True*  
	>Draw only on top of the current layer geometry,
	to avoid accidentally covering previous layers.
	- **Scene** *: ( Scene )*  
	- **Normal Depth** *: ( Texture )*  
	- **ID** *: ( Texture )*  
