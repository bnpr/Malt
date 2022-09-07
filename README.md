# Malt

Malt is a fully customizable real-time rendering framework for animation and illustration.  
It's aimed at advanced users and technical artists who want more control over their workflow and/or their art style, with special care put into the needs of stylized non photorealistic rendering.

[Download](#install) | [Docs](https://malt3d.com) | [Forums & Support](https://github.com/bnpr/Malt/discussions) | [Bug Reports](https://github.com/bnpr/Malt/issues) | [Twitter](https://twitter.com/pragma37) | [Patreon](https://patreon.com/pragma37)

## Features

- **Free and Open Source**. MIT License.
- **Real Time Rendering**.
- **Complete *Blender* integration**.
- **Built-in Pipeline for Stylized Non Photorealistic Rendering**.
- **Code as a First Class Citizen**
    - Automatic reloading.
    - *VSCode* integration, including *GLSL* autocompletion.
    - Automatic generation of nodes from *GLSL* functions.
    - Automatic UI for *Shader* and *Pipeline* parameters.
    - 100% customizable *Python* Render Pipelines.

## Current State

We've been working on a full redesign of the default nodes before the 1.0 Release.  
[Give it try and leave your feedback](https://github.com/bnpr/Malt/discussions/382).

Malt is software agnostic, but Blender is the only integration planned right now.

## Requirements

- OpenGL 4.1+
- Blender 3.3
- Windows or Linux

> A dedicated Nvidia or AMD graphics card is highly recomended.  

## Install
 
- Go to [the latest Release page](https://github.com/bnpr/Malt/releases/tag/Release-latest).
- Download the *BlenderMalt* version that matches your OS.
- Open Blender. Go to *Preferences > Addons*, click on the *Install...* button and select *BlenderMalt.zip* from your downloads. *(It will take a few seconds)*
- Tick the box in the *BlenderMalt* panel to enable it.

> Altenatively, you can download the [Development version](https://github.com/bnpr/Malt/releases/tag/Development-latest) to test the latest features.       

## Uninstall

- Untick the box in *Preferences > Addons > BlenderMalt* to disable the addon.
- Restart *Blender*.
- Go back to *Preferences > Addons > BlenderMalt*, expand the panel and click the *Remove* button.

## First steps

To learn how to use *Malt*, check the [Docs](https://malt3d.com/Documentation/Getting%20Started/), this [playlist](https://www.youtube.com/playlist?list=PLiN2BGdwwlLqbks8h5MohvH0Xd0Zql_Sg) and the [Sample Files](https://github.com/bnpr/Malt/discussions/94).  
The [Q&A section](https://github.com/bnpr/Malt/discussions/categories/q-a) is full of info as well.

## Developer Documentation

[How to setup BlenderMalt for Development.](docs/Setup-BlenderMalt-for-Development.md)

Developer documentation is best viewed directly in [Github](https://github.com/bnpr/Malt/tree/Development#developer-documentation), most folders in the source code have relevant documentation.  
The [Malt folder documentation](Malt#malt) is a good starting point.

