# FAQ

# Will Malt or BEER have nodes?

A node based UI for Malt is planned for the medium term.
Please note that compatibility with EEVEE/Cycles nodes is out of scope.

BEER will have a layers/stack based UI.

# What's the difference between Malt and BEER?

|   | Malt | BEER |
|---|------|------|
| **Target Audience** | Advanced users | Everyone |
| **Worflow** | Code <br> (Nodes planned) | Layers/Stacks |
| **Backend** | None <br> (Built from scratch) | Malt |
| **Project Lead** | [Miguel Pozo](https://twitter.com/pragma37) | [LightBWK](https://twitter.com/Lightbwk) |
| **Main Developer** | [Miguel Pozo](https://twitter.com/pragma37) | TBD |
| **Funding** | [Patreon](https://patreon.com/pragma37) | [BEER Dev Fund](https://blendernpr.org/beer/) |

# Will Malt be ported to Vulkan?

The most likely replacement for OpenGL in Malt would be WebGPU Native (assuming everything goes well and WebGPU gets approved as a web standard) since it seems easier to use than Vulkan and we could still support MacOS while having newer gpu features available.

The only real advantage at the moment for switching to Vulkan would be hardware ray tracing, which is still unsupported by most hardware.

So the long story short is that we will stay with OpenGL until we have a good reason to switch.

# Can Malt be used for games?

Not at the moment.

The shader library can be a good fit for other engines that can run GLSL shaders, but Malt as a whole is not a good fit for games.

Malt main focus is animation and illustration and it prioritizes flexibility and image quality, which usually comes at a performance cost.

# How can I contribute?

- Make art with Malt and share it.
- Make tutorials.
- Improve the documentation.
- Implement new features.
- Join the Malt Gallery program.
- Fund the project.

