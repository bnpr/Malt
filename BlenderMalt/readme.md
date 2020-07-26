# Malt

Malt is a highly customizable rendering framework written in Python and OpenGL.<br>
BlenderMalt is a Blender addon that integrates Malt into Blender, exposing a minimal user interface suitable for a code-centric workflow.

Malt will serve as the backbone of BEER, the BlenderNPR render engine.<br>
https://blendernpr.org/beer/

Malt allows to write completely custom render pipelines while providing a flexible library of render utilities.<br>
BlenderMalt takes care of exposing the UI for your pipeline and manages all the render data loading and synchronization.

## Installation

*(Malt is still in early development state)*

BlenderMalt is distributed as a normal Blender addon.

*(For F12 rendering to work you need Blender 2.9 beta or later. Alternatively you can also download a custom release build from [here](https://github.com/pragma37/Blender-NPR/actions), wich also includes Freestyle support.)*

To download and install it: 
- Go to [the repository Actions page](https://github.com/blendernpr/BEER/actions) and click on the latest event.
- Download the *BlenderMalt* artifact. **(You have to be logged in Github to download it)**
  - *(Optional)* Download the *Shader Examples* too.
- Open Blender. Go to *Preferences > Addons*, click on the *Install...* button and select *BlenderMalt.zip* from your downloads.
- Search for *BlenderMal*t on the addons list and enable it.<br>
  - BlenderMalt needs to download a few dependencies the first time you enable it, so **Blender will freeze for a few seconds**.
  - If you want to see the installation process you can click on *Window > Toggle System Console* before enabling the addon.
  - **You might have to open Blender with administrator privileges if it's installed on a protected path.**(Like the Windows ProgramData folder)
- Restart Blender.

To test the renderer go to Scene Settings and change the renderer to Malt. Create a Sunlight and add a new object with a new material. Inside the material settings set the Shader Path to one of the files from the Shader Examples.

If you need help you can ask on the [project issues page](https://github.com/BlenderNPR/BEER/issues).
