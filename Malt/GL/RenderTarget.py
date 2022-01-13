import ctypes

from Malt.GL.GL import *


class RenderTarget():

    def __init__(self, targets=[], depth_stencil=None):
        self.FBO = gl_buffer(GL_INT, 1)
        glGenFramebuffers(1, self.FBO)

        self.targets = targets
        self.depth_stencil = depth_stencil

        self.resolution = None

        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO[0])

        attachments = gl_buffer(GL_INT, len(targets))
        for i, target in enumerate(targets):
            if target:
                if self.resolution is None : self.resolution = target.resolution
                assert(target.resolution == self.resolution)
                if hasattr(target, 'attach'):
                    target.attach(GL_COLOR_ATTACHMENT0+i)
                else:
                    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0+i, GL_TEXTURE_2D, target.texture[0], 0)
                attachments[i] = GL_COLOR_ATTACHMENT0+i
            else:
                attachments[i] = GL_NONE
        
        glDrawBuffers(len(attachments), attachments)
        
        if depth_stencil:
            if self.resolution is None : self.resolution = depth_stencil.resolution
            assert(depth_stencil.resolution == self.resolution)
            attachment = {
                GL_DEPTH_STENCIL : GL_DEPTH_STENCIL_ATTACHMENT,
                GL_DEPTH_COMPONENT : GL_DEPTH_ATTACHMENT,
                GL_STENCIL : GL_STENCIL_ATTACHMENT,
            }
            if hasattr(depth_stencil, 'attach'):
                depth_stencil.attach(attachment[depth_stencil.format])
            else:
                glFramebufferTexture2D(GL_FRAMEBUFFER, attachment[depth_stencil.format], GL_TEXTURE_2D, depth_stencil.texture[0], 0)
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO[0])
        glViewport(0, 0, self.resolution[0], self.resolution[1])
        glDisable(GL_SCISSOR_TEST)
    
    def clear(self, colors=[], depth=None, stencil=None):
        self.bind()
        flags = 0
        for i, color in enumerate(colors):
            function_map = {
                GL_INT : glClearBufferiv,
                GL_UNSIGNED_INT : glClearBufferuiv,
                GL_FLOAT : glClearBufferfv,
                GL_UNSIGNED_BYTE : glClearBufferfv,
            }
            target = self.targets[i]
            if target is None:
                continue
            if isinstance(color, ctypes.Array) == False:
                size = 1
                try: size = len(color)
                except: pass
                color = gl_buffer(target.data_format, size, color)
            function_map[target.data_format](GL_COLOR, i, color)
        if depth:
            glClearDepth(depth)
            flags |= GL_DEPTH_BUFFER_BIT
        if stencil:
            glClearStencil(stencil)
            flags |= GL_STENCIL_BUFFER_BIT
        glClear(flags)
    
    def __del__(self):
        glDeleteFramebuffers(1, self.FBO)


class TargetBase():
    def attach(self, attachment):
        pass


class ArrayLayerTarget(TargetBase):
    def __init__(self, texture_array, layer):
        self.texture_array = texture_array.texture[0]
        self.layer = layer
        self.resolution = texture_array.resolution
        self.internal_format = texture_array.internal_format
        self.format = texture_array.format
        self.data_format = texture_array.data_format
    
    def attach(self, attachment):
        glFramebufferTextureLayer(GL_FRAMEBUFFER, attachment, self.texture_array, 0, self.layer)

