# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy

from Malt import GL
from Malt import Texture

__GRADIENTS = {}
__GRADIENT_RESOLUTION = 256

# WORKAROUND: We can't declare color ramps from python,
# so we store them as nodes inside a material
def get_color_ramp(material, name):
    #TODO: Create a node tree for each ID with Malt Properties to store ramps ??? (Node Trees are ID types)
    '''
    if '__MALT_COLOR_RAMPS_INTERNAL__' not in bpy.data.materials:
        material = bpy.data.materials.new('__MALT_COLOR_RAMPS_INTERNAL__')
        material.use_nodes = True
        material.use_fake_user = True
    '''
    if material.use_nodes == False:
        material.use_nodes = True
    nodes = material.node_tree.nodes

    if name not in nodes:
       node = nodes.new('ShaderNodeValToRGB')
       node.name = name
    
    return nodes[name]


def get_color_ramp_texture(material, name):
    node = get_color_ramp(material, name)
    #pixels = [0,0,0,0]*__GRADIENT_RESOLUTION
    pixels = []
    if material.name_full not in __GRADIENTS:
        __GRADIENTS[material.name_full] = {}
    gradients = __GRADIENTS[material.name_full]
    if name not in gradients:
        for i in range(0, __GRADIENT_RESOLUTION):
            pixel = node.color_ramp.evaluate( i*(1.0 / __GRADIENT_RESOLUTION))
            pixels.extend(pixel)
        nearest = node.color_ramp.interpolation == 'CONSTANT'
        gradients[name] = Texture.Gradient(pixels, __GRADIENT_RESOLUTION, nearest_interpolation=nearest)
    
    return gradients[name]



# WORKAROUND: For some reason bpy.types.Image can't be used directly in CollectionProperty, 
# although it's an ID type, so we wrap it inside a PropertyGroup
class MaltTexturePropertyWrapper(bpy.types.PropertyGroup):

    texture : bpy.props.PointerProperty(type=bpy.types.Image)

class MaltPropertyGroup(bpy.types.PropertyGroup):

    # Textures are not fully supported in Custom Properties,
    # so we store them here and its metadata in _RNA_UI.
    # Textures can be acessed by name, i.e. textures["image_name"]
    textures : bpy.props.CollectionProperty(type=MaltTexturePropertyWrapper)

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
                # We treat underscored and all caps uniforms as "private"
                continue

            if name not in rna.keys():
                rna[name] = {}
            
            rna[name]['active'] = True
            
            if uniform.type == GL.GL_SAMPLER_2D:
                if name not in self.textures:
                    self.textures.add().name = name
                if name in self.keys():
                    self.pop(name)
                rna[name]['type'] = uniform.type            
                continue

            if uniform.type == GL.GL_SAMPLER_1D:
                get_color_ramp(self.id_data, name)
            
            is_default = name in self.keys() and 'default' in rna[name].keys() and rna[name]['default'][:] == self[name][:]
            type_changed = name in self.keys() and 'type' in rna[name].keys() and rna[name]['type'] != uniform.type

            if name not in self.keys() or is_default or type_changed:
                self[name] = uniform.value
            
            rna[name]["default"] = uniform.value
            rna[name]['type'] = uniform.type

            #TODO: for now we assume we want floats as colors
            # ideally it should be opt-in in the UI,
            # so we can give them propper min/max values
            if uniform.base_type in (GL.GL_FLOAT, GL.GL_DOUBLE):
                rna[name]['subtype'] = 'COLOR'
                rna[name]['use_soft_limits'] = True
                rna[name]['soft_min'] = 0.0
                rna[name]['soft_max'] = 1.0
            else:
                rna[name]['subtype'] = 'NONE'
                rna[name]['use_soft_limits'] = False
        
        # Force a depsgraph update. 
        # Otherwise these won't be available inside scene_eval
        self.id_data.update_tag()
    

    def get_parameters(self):
        if '_RNA_UI' not in self.keys():
            return {}
        rna = self.get_rna()
        parameters = {}
        for key in rna.keys():
            if rna[key]['active'] == False:
                continue
            parameters[key] = self[key]
        return parameters

    
    def draw_ui(self, layout):
        layout.label(text="Malt Properties")
        if '_RNA_UI' not in self.keys():
            return #Can't modify ID classes from here
        rna = self.get_rna()
        
        #TODO: Order in a predictable way ?
        for key in rna.keys():
            if rna[key]['active'] == False:
                continue
            
            if rna[key]['type'] == GL.GL_SAMPLER_2D:
                layout.label(text=key + " :")
                row = layout.row()
                row = row.split(factor=0.8)
                row.template_ID(self.textures[key], "texture", new="image.new", open="image.open")
                if self.textures[key].texture:
                    row.prop(self.textures[key].texture.colorspace_settings, 'name', text='')
            elif rna[key]['type'] == GL.GL_SAMPLER_1D:
                layout.label(text=key + " :")
                layout.template_color_ramp(get_color_ramp(self.id_data, key), 'color_ramp')
            else:
                #TODO: add subtype toggle
                layout.prop(self, '["'+key+'"]')



class MALT_PT_Base(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "disabled"

    bl_label = "Malt Settings"
    COMPAT_ENGINES = {'MALT'}

    @classmethod
    def get_malt_property_owner(cls, context):
        return None

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT' and cls.get_malt_property_owner(context)
    
    def draw(self, context):
        owner = self.__class__.get_malt_property_owner(context)
        if owner:
            owner.malt_parameters.draw_ui(self.layout)


class MALT_PT_Scene(MALT_PT_Base):
    bl_context = "scene"
    @classmethod
    def get_malt_property_owner(cls, context):
        return context.scene

class MALT_PT_World(MALT_PT_Base):
    bl_context = "world"
    @classmethod
    def get_malt_property_owner(cls, context):
        return context.scene.world

class MALT_PT_Camera(MALT_PT_Base):
    bl_context = "data"
    @classmethod
    def get_malt_property_owner(cls, context):
        if context.object.type == 'CAMERA':
            return context.object.data
        else:
            return None

class MALT_PT_Object(MALT_PT_Base):
    bl_context = "object"
    @classmethod
    def get_malt_property_owner(cls, context):
        return context.object

class MALT_PT_Light(MALT_PT_Base):
    bl_context = "data"
    @classmethod
    def get_malt_property_owner(cls, context):
        if context.object.type == 'LIGHT':
            return context.object.data
        else:
            return None
    def draw(self, context):
        layout = self.layout
        owner = self.__class__.get_malt_property_owner(context)
        if owner and owner.type != 'AREA':
            '''
            layout.prop(owner, 'color')
            if owner.type == 'POINT':
                layout.prop(owner, 'shadow_soft_size', text='Radius')
            elif owner.type == 'SPOT':
                layout.prop(owner, 'cutoff_distance', text='Distance')
                layout.prop(owner, 'spot_size', text='Spot Angle')
                layout.prop(owner, 'spot_blend', text='Spot Blend')
            '''
            owner.malt.draw_ui(layout)
            owner.malt_parameters.draw_ui(layout)

classes = (
    MaltTexturePropertyWrapper,
    MaltPropertyGroup,
    MALT_PT_Base,
    MALT_PT_Scene,
    MALT_PT_World,
    MALT_PT_Camera,
    MALT_PT_Object,
    MALT_PT_Light,
)

@bpy.app.handlers.persistent
def depsgraph_update(scene, depsgraph):
    for update in depsgraph.updates:
        #if isinstance(update.id, bpy.types.NodeTree):
        if update.id.__class__ == bpy.types.Material:
            __GRADIENTS[update.id.name_full] = {}
            for screen in bpy.data.screens:
                for area in screen.areas:
                    area.tag_redraw()


def register():
    for _class in classes: bpy.utils.register_class(_class)

    bpy.types.Scene.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup)
    bpy.types.World.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup)
    bpy.types.Camera.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup)
    bpy.types.Object.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup)
    bpy.types.Material.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup)
    bpy.types.Light.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup)

    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update)


def unregister():
    for _class in classes: bpy.utils.unregister_class(_class)

    del bpy.types.Scene.malt_parameters
    del bpy.types.World.malt_parameters
    del bpy.types.Camera.malt_parameters
    del bpy.types.Object.malt_parameters
    del bpy.types.Material.malt_parameters
    del bpy.types.Light.malt_parameters

    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update)


