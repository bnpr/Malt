from Malt.PipelineParameters import Parameter

MATERIAL_SHADERS = {}

class Material():

    def __init__(self, path, pipeline, search_paths=[], custom_passes={}):
        self.path = path
        self.parameters = {}
        self.compiler_error = ''
        
        compiled_material = pipeline.compile_material(path, search_paths)#, custom_passes)
        
        if isinstance(compiled_material, str):
            self.compiler_error = compiled_material
        else:
            for pass_name, shader in compiled_material.items():
                for uniform_name, uniform in shader.uniforms.items():
                    self.parameters[uniform_name] = Parameter.from_uniform(uniform)
                if shader.error:
                    self.compiler_error += pass_name + " : " + shader.error
                if shader.validator:
                    self.compiler_error += pass_name + " : " + shader.validator
        
        if self.compiler_error == '':
            global MATERIAL_SHADERS
            MATERIAL_SHADERS[self.path] = compiled_material
        else:
            MATERIAL_SHADERS[self.path] = {}


def get_shader(path, parameters):
    if path not in MATERIAL_SHADERS.keys():
        return {}
    shaders = MATERIAL_SHADERS[path]
    new_shader = {}

    for pass_name, pass_shader in shaders.items():
        if pass_shader.error:
            new_shader = {}
            break

        pass_shader_copy = pass_shader.copy()
        new_shader[pass_name] = pass_shader_copy

        for name, parameter in parameters.items():
            if name in pass_shader_copy.textures.keys():
                pass_shader_copy.textures[name] = parameter
            elif name in pass_shader_copy.uniforms.keys():
                pass_shader_copy.uniforms[name].set_value(parameter)
    
    return new_shader




