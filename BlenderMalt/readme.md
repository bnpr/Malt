# BlenderMalt

## Introduction

*BlenderMalt* is a [*Malt Host*](../Malt#malt-pipelines) for *Blender*.  
It handles all the *Scene* data loading and syncronization and exposes a minimal UI suitable for a code-centric workflow.  
*BlenderMalt* communicates with *Malt* through a [*Bridge*](../Bridge) instance.  

## RenderEngine

[*MaltRenderEngine.py*](MaltRenderEngine.py) implements the *Blender* [*RenderEngine*](https://docs.blender.org/api/current/bpy.types.RenderEngine.html) interface.

It takes care of generating a *Malt Scene* from the *Blender* [*DepsGraph*](https://docs.blender.org/api/current/bpy.types.Depsgraph.html), send it to *Bridge* for rendering and pass the result back to *Blender*.

## Pipeline

[*MaltPipeline.py*](MaltPipeline.py) handles *Bridge* instances, makes sure all *Blender* objects have their respective *Pipeline Parameters* registered as *MaltPropertyGroups*, and handles *Meshes* and *Textures* updates.

## Pipeline Properties

[*MaltPropertyGroups*](MaltProperties.py) store *Malt* *Pipeline Parameters* as native *Blender* [*PropertyGroups*](https://docs.blender.org/api/current/bpy.types.PropertyGroup.html) and convert them to *Malt* *Scene* parameters on request.
They also can handle their own UI rendering automatically, all that is needed is to pass a *Blender* [*UI Layout*](https://docs.blender.org/api/current/bpy.types.UILayout.html) to their *draw_ui* method.

## Materials

[*MaltMaterial.py*](MaltMaterial.py) handles the compilation (including automatic hot-reloading), UI rendering and storage as native *Blender* materials of *Malt* *Pipeline* materials.

## Meshes

[*MaltMeshes.py*](MaltMeshes.py) retrieves any *Blender* geometry as vertex and index buffers and sends it to *Bridge*.  
This module is highly optimized to allow real-time mesh editing and (when possible) retrieves vertex data directly from *Blender* internal C data through the [*CBlenderMalt*](CBlenderMalt) library.

## Textures

[*MaltTextures.py*](MaltTextures.py) sends 1D and 2D textures pixel data to *Bridge*.  

