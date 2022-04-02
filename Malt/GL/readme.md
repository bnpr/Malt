# GL

The GL folder contains a series of modules that abstracts commonly needed OpenGL functionality.  
It doesn't try to be a complete abstraction, so it's meant to be used alongside raw OpenGL calls.  
> 💡 Malt limits itself to OpenGL 4.1 features to keep MacOS compatibility.

## [GL.py](GL.py) 
Loads OpenGL functions via [PyOpenGL](https://pypi.org/project/PyOpenGL/), provides OpenGL enums reflection dictionaries and implements a Python to OpenGL types conversion function via the *gl_buffer function*.

## [Mesh.py](Mesh.py)

Builds VAOs with the same layout used by [Common.glsl](Malt/Shaders/Common.glsl).  
Each parameter expects a flat 1D iterable with all the per-vertex data.  
Tangents, UVs and Vertex Colors buffers must be passed inside a list, even if you pass only one. Four of each are allowed at most.  

The MeshCustomLoad class doesn't do any loading by itself. It's reserved for cases where special opimizations are needed, like [BlenderMalt/MaltMeshes.py](BlenderMalt/MaltMeshes.py).  

* [OpenGL Wiki - Vertex Array Object](https://www.khronos.org/opengl/wiki/Vertex_Specification#Vertex_Array_Object)
* [LearnOpenGL - Hello Triangle](https://learnopengl.com/Getting-started/Hello-Triangle)

## [Shader.py](Shader.py)

Builds OpenGL programs from GLSL vertex and fragment shader source code and provides an interface for reflection and configuration of shader parameters.  

The *shader_preprocessor* function parses source code with a C preprocessor to provide support for *#include directives* in glsl shaders.  

* [OpenGL Wiki - GLSL Objects](https://www.khronos.org/opengl/wiki/GLSL_Object)
* [Learn OpenGL - Shaders](https://learnopengl.com/Getting-started/Shaders)

## [Texture.py](Texture.py)

Loads 1D textures (*Gradient*), 2D textures (*Texture*), 2D texture arrays (*TextureArray*), cube maps (*CubeMap*) and cube map arrays (*CubeMapArrays*) under a simple and mostly shared interface.  
The *internal_format* parameter is the [OpenGL image format](https://www.khronos.org/opengl/wiki/Image_Format) the texture will be stored inside the GPU.

* [OpenGL Wiki - Texture](https://www.khronos.org/opengl/wiki/Texture)
* [Learn OpenGL - Textures](https://learnopengl.com/Getting-started/Textures)

## [RenderTarget.py](RenderTarget.py)

Builds FBOs from Textures. It accepts an arbitrary number of color targets and a single depth/stencil target.  
Color target Textures must be passed inside a list, even if you pass only one.  

For rendering to other types of targets (like Cube Maps and Texture Arrays) you can pass an object with a custom attach method (See the *ArrayLayerTarget* class for an example).  

* [OpenGL Wiki - Framebuffer Objects](https://www.khronos.org/opengl/wiki/Framebuffer_Object)
* [Learn OpenGL - Framebuffers](https://learnopengl.com/Advanced-OpenGL/Framebuffers)

## Basic Example (draw a full screen quad)

```python
positions=[
     1.0,  1.0, 0.0,
     1.0, -1.0, 0.0,
    -1.0, -1.0, 0.0,
    -1.0,  1.0, 0.0,
]
indices=[
    0, 1, 3,
    1, 2, 3,
]

mesh = Mesh(positions, indices)

vertex_source='''
layout (location = 0) in vec3 POSITION;
void main()
{
    gl_Position = vec4(POSITION, 1);
}
'''

pixel_source='''
layout (location = 0) out vec4 RESULT;
uniform vec4 color = vec4(1,0,0,1);
void main()
{
    RESULT = color;
}
'''

shader = Shader(vertex_source, pixel_source)

shader.uniforms['color'].set_value((0,1,0,1))

result_texture = Texture((1024, 1024), GL_RGBA32F)

result_target = RenderTarget([result_texture])

result_target.bind()
shader.bind()
mesh.draw()
```

