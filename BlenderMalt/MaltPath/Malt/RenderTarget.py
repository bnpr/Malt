# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from Malt.GL import *
import ctypes

class TargetBase(object):
    def attach(self, index):
        pass

class ArrayLayerTarget(TargetBase):
    def __init__(self, texture_array, layer):
        self.texture_array = texture_array.texture[0]
        self.layer = layer
        self.resolution = texture_array.resolution
        self.format = texture_array.format
    
    def attach(self, attachment):
        glFramebufferTextureLayer(GL_FRAMEBUFFER, attachment, self.texture_array, 0, self.layer)

class RenderTarget(object):

    def __init__(self, targets=[], depth_stencil=None):
        self.FBO = gl_buffer(GL_INT, 1)
        glGenFramebuffers(1, self.FBO)

        self.targets = targets
        self.depth_stencil = depth_stencil

        self.resolution = (0,0)
        if len(targets) > 0:
            self.resolution = targets[0].resolution
        else:
            self.resolution = depth_stencil.resolution

        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO[0])

        attachments = gl_buffer(GL_INT, len(targets))
        for i, target in enumerate(targets):
            assert(target.resolution == self.resolution)
            if hasattr(target, 'attach'):
                target.attach(GL_COLOR_ATTACHMENT0+i)
            else:
                glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0+i, GL_TEXTURE_2D, target.texture[0], 0)
            attachments[i] = GL_COLOR_ATTACHMENT0+i
        
        glDrawBuffers(len(attachments), attachments)
        
        if depth_stencil:
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
            }
            target = self.targets[i]
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
        try:
            glDeleteFramebuffers(1, self.FBO)
        except:
            #TODO: Make sure GL objects are deleted in the correct context
            pass

