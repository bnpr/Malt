# Malt

Malt is a fully customizable real-time rendering framework for animation and illustration.  
It's aimed at advanced users and technical artists who want more control over their workflow and/or their art style, with special care put into the needs of stylized non photorealistic rendering.

[Docs](https://malt3d.com) | [Forums & Support](https://github.com/bnpr/Malt/discussions) | [Bug Reports](#bug-reports) | [Twitter](https://twitter.com/pragma37) | [Patreon](https://patreon.com/pragma37)

### Features

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

Malt development began on June 2020 and it's still in beta state.   
We're getting near the 1.0 Release, take a lookt at [Malt 1.0 UX Improvements](https://github.com/bnpr/Malt/discussions/148) and leave your feedback.

Malt is software agnostic, but Blender is the only integration planned right now.

## Requirements

- OpenGL 4.1 support.
- Latest Blender release.

> A dedicated Nvidia or AMD graphics card is highly recomended.  

> While Malt itself works on Mac, the default render pipeline does not due to limits in the Mac OpenGL drivers.

> On Linux distributions not based on Ubuntu, you may have to compile and package BlenderMalt yourself.     
> See [How to setup BlenderMalt for Development](docs/Setup-BlenderMalt-for-Development.md) for instructions.

## Install
 
- Go to [the latest Release page](https://github.com/bnpr/Malt/releases/tag/Release-latest).
- Download the *BlenderMalt* version that matches your OS.
- Open Blender. Go to *Preferences > Addons*, click on the *Install...* button and select *BlenderMalt.zip* from your downloads. *(It will take a few seconds)*
- Tick the box in the *BlenderMalt* panel to enable it.

> Altenatively, you can download the [Development version](https://github.com/bnpr/Malt/releases/tag/Development-latest) to test the latest features.       
> Keep in mind this version is only intended for testing and your scenes may break often.

#### Uninstall

- Untick the box in *Preferences > Addons > BlenderMalt* to disable the addon.
- Restart *Blender*.
- Go back to *Preferences > Addons > BlenderMalt*, expand the panel and click the *Remove* button.

## First steps

To learn how to make your own materials in *Malt*, take a look at this [Malt Nodes introduction](https://www.youtube.com/watch?v=tE99jgCCcNE) and check the [Sample Files](https://github.com/bnpr/Malt/discussions/94).

> Malt allows to use different settings for *Viewport Preview*, *Viewport Render* and *F12 Render*.  
> By default, the *Viewport Preview* should be faster than the *Viewport Render* mode.

## Bug Reports

If you find a bug you can [open a new issue](https://github.com/bnpr/Malt/issues).

**For bug reports include**:
- The **Log file** from the Blender session where the bug happened. You can find it in *Preferences > Addons > BlenderMalt > Open Session Log* or search for it in your system temporary folder.
- A **.blend file** and a **list of steps** to reproduce the error.

## Developer Documentation

[How to setup BlenderMalt for Development.](docs/Setup-BlenderMalt-for-Development.md)

Developer documentation is best viewed directly in [Github](https://github.com/bnpr/Malt/tree/Development#developer-documentation), most folders in the source code have relevant documentation.  
The [Malt folder documentation](Malt#malt) is a good starting point.

