# NPR Pipeline

The NPR Pipeline is the default Malt Pipeline. It's designed for stylized and NPR rendering.

It features:
- Line Rendering.
- Complete Lighting and Shading control.
- Custom Light Shaders.
- Custom Screen-Space Shaders (wip).

## Settings

> You can reset any setting with *Right Click > Reset to Default Value*.  
> You can add a quality override to any setting by clicking the button on its right side.

### World

- **Background Color**  
The color of the render background. *(transparent backgrounds are not yet supported)*

### Scene

#### Line
- **Max Width**  
The maximum width the line compositing shader can render.  
High values can have a heavy performance impact.

#### Samples
- **Grid Size**  
The number of render samples per side in the sample grid. The total number of samples is the square of this value minus the samples that fall outside of the sampling radius.  
Higher values will provide cleaner renders at the cost of higher render times.
- **Width**  
The size of the sample grid.  
Large values will blur the render while small values will cause aliasing artifacts.

#### ShadowMaps
- **Resolution**  
The resolution of the shadow maps for each light type. For Sun Lights it sets the resolution for each cascade and for Point Lights the resolution for each cubemap side.

##### Sun Cascades
- **Count**  
The number of [Shadow Cascades](https://docs.microsoft.com/en-us/windows/win32/dxtecharts/cascaded-shadow-maps#cascaded-shadow-maps-and-perspective-aliasing) to be rendered.
- **Max Distance**  
The maximum distance from the view origin at which objects will still cast shadows. The lower the value, the higher the perceived resolution.
- **Distribution Scalar**  
Controls the cascades distribution along the view distance, where 0 means linear distribution and 1 logarithmic distribution.  
The appropriate value depends on camera FOV and scene characteristics. You can visualize the Shadow Cascades distribution by applying the debug_cascades.meshs.glsl shader to a plane scaled to cover the full XY extension of the view.

#### Transparency
- **Layers**  
The maximum number of transparent objects that can visualy overlap.  
Each layer has a high fixed performance cost, regardless of how many transparent objects there are in the scene.

### Mesh
- **Double Sided**  
Disables backface culling, so geometry is rendered from both sides.
- **Precomputed Tangents**  
Load mesh tangents, needed for pre-baked normal maps. It's disabled by default since it heavily slows down mesh loading in Blender.

### Material
- **Self Shadow**  
Enable meshes casting shadows onto themselves.
- **Transparency**  
Enable material alpha blending. (Alpha clipping is always enabled for alpha values equal to 0)
- **Single Layer Transparency**  
If enabled, the whole mesh is drawn as a single transparent layer.
- **Shader Source**  
GLSL source file for the material. Its file extension must be```.mesh.glsl```.

### Light

- **Color**  
The light color if no custom shader is in use.
- **Radius**  
The light area of effect radius.  
  *Point* and *Spot Lights.*
- **Angle**  
  *Spot light* cone angle.
- **Blend**  
  *Spot light* cone gradient angle.
- **Shader**  
GLSL source file for the material. Its file extension must be```.light.glsl```.


