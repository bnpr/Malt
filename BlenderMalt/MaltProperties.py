# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy

from Malt import Texture
from Malt.Parameter import *

from BlenderMalt import MaltPipeline

__GRADIENTS = {}
__GRADIENT_RESOLUTION = 256

# WORKAROUND: We can't declare color ramps from python,
# so we store them as nodes inside a material
def get_color_ramp(material, name):
    #TODO: Create a node tree for each ID with Malt Properties to store ramps ??? (Node Trees are ID types)
    
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


class MaltTexturePropertyWrapper(bpy.types.PropertyGroup):

    texture : bpy.props.PointerProperty(type=bpy.types.Image)

class MaltMaterialPropertyWrapper(bpy.types.PropertyGroup):

    material : bpy.props.PointerProperty(type=bpy.types.Material)

class MaltBoolPropertyWrapper(bpy.types.PropertyGroup):

    boolean : bpy.props.BoolProperty()

class MaltPropertyGroup(bpy.types.PropertyGroup):

    bools : bpy.props.CollectionProperty(type=MaltBoolPropertyWrapper)
    textures : bpy.props.CollectionProperty(type=MaltTexturePropertyWrapper)    
    materials : bpy.props.CollectionProperty(type=MaltMaterialPropertyWrapper)

    def get_rna(self):
        if '_RNA_UI' not in self.keys():
            self['_RNA_UI'] = {}
        return self['_RNA_UI']

    def setup(self, parameters):
        rna = self.get_rna()

        #TODO: We should purge non active properties (specially textures)
        # at some point, likely on file save or load 
        # so we don't lose them immediately when changing shaders/pipelines
        for key, value in rna.items():
            rna[key]['active'] = False
        
        for name, parameter in parameters.items():
            if name.isupper() or name.startswith('_'):
                # We treat underscored and all caps uniforms as "private"
                continue

            if name not in rna.keys():
                rna[name] = {}

            type_changed = 'type' not in rna[name].keys() or rna[name]['type'] != parameter.type

            if parameter.type in (Type.INT, Type.FLOAT):
                if type_changed or rna[name]['default'] == self[name]:
                    self[name] = parameter.default_value

            if parameter.type == Type.BOOL:
                if name not in self.bools:
                    self.bools.add().name = name
                if type_changed or rna[name]['default'] == self.bools[name].boolean:
                    self.bools[name].boolean = parameter.default_value
            
            if parameter.type == Type.TEXTURE:
                if name not in self.textures:
                    self.textures.add().name = name

            if parameter.type == Type.GRADIENT:
                get_color_ramp(self.id_data, name)

            if parameter.type == Type.MATERIAL:
                if name not in self.materials:
                    self.materials.add().name = name
                
                shader_path = parameter.default_value
                if shader_path and shader_path != '':
                    if shader_path not in bpy.data.materials:
                        bpy.data.materials.new(shader_path)
                        material = bpy.data.materials[shader_path]
                        material.malt.shader_source = shader_path    
                        material.malt.update_source(bpy.context)
                
                    material = self.materials[name].material
                    if type_changed or (material and rna[name]['default'] == material.malt.shader_source):
                        self.materials[name].material = bpy.data.materials[shader_path]

            rna[name]['active'] = True
            rna[name]["default"] = parameter.default_value
            rna[name]['type'] = parameter.type

            #TODO: for now we assume we want floats as colors
            # ideally it should be opt-in in the UI,
            # so we can give them propper min/max values
            if parameter.type == Type.FLOAT and parameter.size >= 3:
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
            if rna[key]['type'] in (Type.INT, Type.FLOAT):
                parameters[key] = self[key]
            elif rna[key]['type'] == Type.BOOL:
                parameters[key] = self.bools[key].boolean
            elif rna[key]['type'] == Type.TEXTURE:
                texture = self.textures[key].texture
                if texture:
                    texture.gl_load()
                    parameters[key] = texture.bindcode
                else:
                    parameters[key] = None
            elif rna[key]['type'] == Type.GRADIENT:
                #TODO: Only works for materials
                parameters[key] = get_color_ramp_texture(self.id_data, key)
            elif rna[key]['type'] == Type.MATERIAL:
                material = self.materials[key].material
                if material:
                    shader = material.malt.get_shader()
                    if shader:
                        parameters[key] = shader[MaltPipeline.get_pipeline().__class__.__name__]
                else:
                    parameters[key] = None
        return parameters

    
    def draw_ui(self, layout):
        layout.label(text="Malt Properties")
        if '_RNA_UI' not in self.keys():
            return #Can't modify ID classes from here
        rna = self.get_rna()
        
        # Most drivers sort the uniforms in alphabetical order anyway, 
        # so there's no point in tracking the actual index since it doesn't follow
        # the declaration order
        keys = sorted(rna.keys()) 
        
        for key in keys:
            if rna[key]['active'] == False:
                continue
            if rna[key]['type'] in (Type.INT, Type.FLOAT):
                #TODO: add subtype toggle
                layout.prop(self, '["'+key+'"]')
            elif rna[key]['type'] == Type.BOOL:
                layout.prop(self.bools[key], 'boolean', text=key)
            elif rna[key]['type'] == Type.TEXTURE:
                layout.label(text=key + " :")
                row = layout.row()
                row = row.split(factor=0.8)
                row.template_ID(self.textures[key], "texture", new="image.new", open="image.open")
                if self.textures[key].texture:
                    row.prop(self.textures[key].texture.colorspace_settings, 'name', text='')
            elif rna[key]['type'] == Type.GRADIENT:
                layout.label(text=key + " :")
                layout.template_color_ramp(get_color_ramp(self.id_data, key), 'color_ramp')
            elif rna[key]['type'] == Type.MATERIAL:
                layout.label(text=key + " :")
                layout.template_ID(self.materials[key], "material", new="material.new")
                if self.materials[key].material:
                    self.materials[key].material.malt.draw_ui(layout)


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

class MALT_PT_Material(MALT_PT_Base):
    bl_context = "material"
    @classmethod
    def get_malt_property_owner(cls, context):
        if context.object and len(context.object.material_slots) > 0:
            return context.object.material_slots[0].material

class MALT_PT_Mesh(MALT_PT_Base):
    bl_context = "data"
    @classmethod
    def get_malt_property_owner(cls, context):
        if context.object and context.object.data and context.object.type in ('MESH', 'CURVE', 'SURFACE','FONT'):
            return context.object.data

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
    MaltMaterialPropertyWrapper,
    MaltBoolPropertyWrapper,
    MaltPropertyGroup,
    MALT_PT_Base,
    MALT_PT_Scene,
    MALT_PT_World,
    MALT_PT_Camera,
    MALT_PT_Object,
    MALT_PT_Material,
    MALT_PT_Mesh,
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
    bpy.types.Mesh.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup)
    bpy.types.Curve.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup)
    bpy.types.Light.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup)

    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update)


def unregister():
    for _class in classes: bpy.utils.unregister_class(_class)

    del bpy.types.Scene.malt_parameters
    del bpy.types.World.malt_parameters
    del bpy.types.Camera.malt_parameters
    del bpy.types.Object.malt_parameters
    del bpy.types.Material.malt_parameters
    del bpy.types.Mesh.malt_parameters
    del bpy.types.Curve.malt_parameters
    del bpy.types.Light.malt_parameters

    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update)


