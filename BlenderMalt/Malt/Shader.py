# Copyright (c) 2020 BlenderNPR and contributors. MIT license.

from .GL import *

class Shader(object):

    def __init__(self, vertex_source, pixel_source):
        self.program, self.error = compile_gl_program(vertex_source, pixel_source)
        self.uniforms = {}
        if self.error is None:
            self.uniforms = reflect_program_uniforms(self.program)        
    
    def bind(self):
        glUseProgram(self.program)
        for uniform in self.uniforms.values():
            uniform.bind()
