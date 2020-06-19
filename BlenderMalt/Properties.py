# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy

from .Malt import GL

class MaltProperty(object):

    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value


# WORKAROUND: For some reason bpy.types.Image can't be used directly in CollectionProperty, 
# although it's an ID type, so we wrap it inside a PropertyGroup
class TexturePropertyWrapper(bpy.types.PropertyGroup):

    texture : bpy.props.PointerProperty(type=bpy.types.Image)

class MaltPropertyGroup(bpy.types.PropertyGroup):

    # Textures are not fully supported in Custom Properties,
    # so we store them here and its metadata in _RNA_UI.
    # Textures can be acessed by name, i.e. textures["image_name"]
    textures : bpy.props.CollectionProperty(type=TexturePropertyWrapper)

    def get_rna(self):
        if '_RNA_UI' not in self.keys():
            self['_RNA_UI'] = {}
        return self['_RNA_UI']

    def setup(self, properties):
        rna = self.get_rna()

        #TODO: We should purge non active properties (specially textures)
        # at some point, likely on file save or load 
        # so we don't lose them immediately when changing shaders/pipelines
        for key, value in rna.items():
            rna[key]['active'] = False
        
        for name, uniform in properties.items():
            if name.isupper() or name.startswith('_'):
                continue

            if name not in rna.keys():
                rna[name] = {}
            
            is_default = 'default' in rna[name].keys() and rna[name]['default'][:] == self[name][:]
            type_changed = 'type' in rna[name].keys() and rna[name]['type'] != uniform.type

            if name not in self.keys() or is_default or type_changed:
                self[name] = uniform.value
            
            rna[name]['active'] = True
            rna[name]["default"] = uniform.value
            rna[name]['type'] = uniform.type

            #TODO: for now we assume we want floats as colors
            # ideally it should be opt-in in the UI,
            # so we can give them propper min/max values
            if uniform.base_type in (GL.GL_FLOAT, GL.GL_DOUBLE):
                rna[name]['subtype'] = 'COLOR'
            '''
            if 'SAMPLER' in prop_type:
                if name not in self.textures:
                    self.textures.add().name = name
            else:
            '''
    
    def draw_ui(self, layout):
        layout.label(text="Malt Properties")
        if '_RNA_UI' not in self.keys():
            return #Can't modify ID classes from here
        rna = self.get_rna()
        
        for key in rna.keys():
            if rna[key]['active'] == False or key.startswith("_"):
                # We treat underscored uniforms as "private"
                continue
            '''
            if 'SAMPLER' in rna[key]['type']:
                layout.prop(self.textures[key], 'texture')
            else:
            '''
            layout.prop(self, '["'+key+'"]')
            #TODO: add subtype toggle


classes = (
    TexturePropertyWrapper,
    MaltPropertyGroup,
)

def register():
    for _class in classes: bpy.utils.register_class(_class)


def unregister():
    for _class in classes: bpy.utils.unregister_class(_class)

