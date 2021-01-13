# NPR Pipeline

The NPR Pipeline is the default Malt Pipeline. It's designed for stylized and NPR rendering.

It features:
- Line Rendering.
- Complete Lighting and Shading control.
- Custom Light Shaders.
- Custom Screen-Space Shaders (wip).

## Settings

> You can reset any setting with *Right Click > Reset to Default Value*.

### World

- **Background Color** <br>
The color of the render background. *(transparent backgrounds are not yet supported)*

### Scene

- **Line Width Max** <br>
The maximum width the line compositing shader can render.  
High values can have a heavy performance impact.
- **Sample Grid Size** <br>
The number of render samples per side in the sample grid. The total number of samples is the square of this value minus the samples that fall outside of the sampling radius.  
Higher values will provide cleaner renders at the cost of higher render times.
- **Samples Width** <br>
The size of the sample grid.  
Large values will blur the render while small values will cause aliasing artifacts.
- **Shadow Cascades Distribution Exponent** <br>
Controls the distribution of the Sun Lights shadow resolution along the viewport clipping planes.
The appropriate value depends on camera FOV and scene characteristics. You can visualize the Shadow Cascades distribution by applying the debug_cascades.meshs.glsl shader to a plane scaled to cover the full XY extension of the view.
- **ShadowMaps Resolution** <br>
The resolution of the shadow maps for each light type. For Sun Lights it sets the resolution for each cascade and for Point Lights the resolution for each cubemap side.
- **Transparency Layers** <br>
The maximum number of transparent objects that can visualy overlap.  
Each layer has a high fixed performance cost, regarless of how many transparent objects there are in the scene.

### Mesh

- **Double Sided** <br>
Disables backface culling, so geometry is rendered from both sides.
- **Precomputed Tangents** <br>
Load mesh tangents, needed for pre-baked normal maps. It's disabled by default since it heavily slows down mesh loading in Blender.

### Material

- **Self Shadow** <br>
Enable meshes casting shadows onto themselves.
- **Transparency** <br>
Enable material alpha blending. (Alpha clipping is always enabled for alpha values equal to 0)
- **Single Layer Transparency** <br>
If enabled, the whole mesh is drawn as a single transparent layer.
- **Shader Source** <br>
GLSL source file for the material. Its file extension must be```.mesh.glsl```.

### Light

- **Color** <br>
The light color if no custom shader is in use.
- **Radius** <br>
The light area of effect radius.
 *Point* and *Spot Lights.*
- **Angle** <br>
 *Spot light* cone angle.
- **Blend** <br>
 *Spot light* cone gradient angle.
- **Shader** <br>
GLSL source file for the material. Its file extension must be```.light.glsl```.


