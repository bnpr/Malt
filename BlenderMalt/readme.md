# BlenderMalt

## Introduction

*BlenderMalt* is a [*Malt Host*](../Malt#malt-pipelines) for *Blender*.
It handles all the *Scene* data loading and syncronization and exposes a minimal UI suitable for a code-centric workflow.

## RenderEngine

[*MaltRenderEngine.py*](MaltRenderEngine.py) implements the *Blender* [*RenderEngine*](https://docs.blender.org/api/current/bpy.types.RenderEngine.html) interface.

Each *MaltRenderEngine* instance has its own *Malt Pipeline* instance.  
It takes care of generating a *Malt Scene* from the *Blender* [*DepsGraph*](https://docs.blender.org/api/current/bpy.types.Depsgraph.html) with their respective *Meshes*,*Shaders* and *Pipeline Properties*, send it to the *Malt Pipeline* for rendering and pass the result back to *Blender*.

## Pipeline Properties

[*MaltPipeline.py*](MaltPipeline.py) makes sure all *Blender* objects have their respective *Pipeline Parameters* registered as *MaltPropertyGroups*.

[*MaltPropertyGroups*](MaltProperties.py) store *Malt* *Pipeline Parameters* as native *Blender* [*PropertyGroups*](https://docs.blender.org/api/current/bpy.types.PropertyGroup.html) and convert them to *Malt* *Scene* parameters on request.
They also can handle their own UI rendering automatically, all that is needed is to pass a *Blender* [*UI Layout*](https://docs.blender.org/api/current/bpy.types.UILayout.html) to their *draw_ui* method.

## Materials

[*MaltMaterials*](MaltMaterials.py) handles the compilation (including automatic hot-reloading), UI rendering and storage as native *Blender* materials of *Malt* *Pipeline* materials.

## Meshes

[*MaltMeshes.py*](MaltMeshes.py) loads any *Blender* geometry to *OpenGL* with the same vertex layout used by *Malt*.  
This module is highly optimized to allow real-time mesh editing and (when possible) retrieves vertex data directly from *Blender* internal C data through the [*CBlenderMalt*](CBlenderMalt) library.

## Textures

Textures are uploaded to *OpenGL* directly by [*Blender*](https://docs.blender.org/api/current/bpy.types.Image.html?highlight=gl_load#bpy.types.Image.gl_load), with the only exception being 1D textures (*Gradients/Color Ramps*), that are generated and loaded directly by BlenderMalt in [*MaltProperties.py*](MaltProperties.py).
