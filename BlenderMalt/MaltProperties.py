# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from re import split
import bpy

from Malt.Parameter import *
from Malt import Scene

from BlenderMalt import MaltTextures

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

class MaltTexturePropertyWrapper(bpy.types.PropertyGroup):

    texture : bpy.props.PointerProperty(type=bpy.types.Image)

class MaltMaterialPropertyWrapper(bpy.types.PropertyGroup):

    material : bpy.props.PointerProperty(type=bpy.types.Material)
    extension : bpy.props.StringProperty()

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

    def setup(self, parameters, replace_parameters=True):
        rna = self.get_rna()
        
        def setup_parameter(name, parameter):
            if name not in rna.keys():
                rna[name] = {}

            type_changed = 'type' not in rna[name].keys() or rna[name]['type'] != parameter.type
            size_changed = 'size' in rna[name].keys() and rna[name]['size'] != parameter.size

            def to_basic_type(value):
                try: return tuple(value)
                except: return value
            def equals(a, b):
                return to_basic_type(a) == to_basic_type(b)

            def resize():
                if parameter.size == 1:
                       self[name] = self[name][0]
                else:
                    if rna[name]['size'] > parameter.size:
                        self[name] = self[name][:parameter.size]
                    else:
                        first = self[name]
                        try: first = list(first)
                        except: first = [first]
                        second = list(parameter.default_value)
                        self[name] = first + second[rna[name]['size']:]

            if parameter.type in (Type.INT, Type.FLOAT):
                if type_changed or equals(rna[name]['default'], self[name]):
                    self[name] = parameter.default_value   
                elif size_changed:
                    resize()

            if parameter.type == Type.BOOL:
                if name not in self.bools:
                    self.bools.add().name = name
                if type_changed or equals(rna[name]['default'], self.bools[name].boolean):
                    self.bools[name].boolean = parameter.default_value
                elif size_changed:
                    resize()
            
            if parameter.type == Type.TEXTURE:
                if name not in self.textures:
                    self.textures.add().name = name

            if parameter.type == Type.GRADIENT:
                get_color_ramp(self.id_data, name)

            if parameter.type == Type.MATERIAL:
                if name not in self.materials:
                    self.materials.add().name = name
                
                self.materials[name].extension = parameter.extension
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
            rna[name]['size'] = parameter.size
            rna[name]['filter'] = parameter.filter
        
        #TODO: We should purge non active properties (specially textures)
        # at some point, likely on file save or load 
        # so we don't lose them immediately when changing shaders/pipelines
        if replace_parameters:
            for key, value in rna.items():
                if '@' not in key:
                    rna[key]['active'] = False
        
        for name, parameter in parameters.items():
            if name.isupper() or name.startswith('_'):
                # We treat underscored and all caps uniforms as "private"
                continue
            setup_parameter(name, parameter)

        for key, value in rna.items():
            if '@' in key and key not in parameters.keys():
                main_name = key.split(' @ ')[0]
                rna[key]['active'] = rna[main_name]['active'] and rna[key]['active']
                if rna[key]['active']:
                    parameter = Parameter(rna[main_name]['default'], rna[main_name]['type'], rna[main_name]['size'])
                    setup_parameter(key, parameter)
        
        for key, value in rna.items():
            #TODO: for now we assume we want floats as colors
            # ideally it should be opt-in in the UI,
            # so we can give them propper min/max values
            if rna[key]['type'] == Type.FLOAT and rna[key]['size'] >= 3:
                rna[key]['subtype'] = 'COLOR'
                rna[key]['use_soft_limits'] = True
                rna[key]['soft_min'] = 0.0
                rna[key]['soft_max'] = 1.0
            else:
                rna[key]['subtype'] = 'NONE'
                rna[key]['use_soft_limits'] = False

        # Force a depsgraph update. 
        # Otherwise these won't be available inside scene_eval
        self.id_data.update_tag()
        for screen in bpy.data.screens:
            for area in screen.areas:
                area.tag_redraw()
    
    def add_override(self, property_name, override_name):
        main_prop = self.get_rna()[property_name]
        new_name = property_name + ' @ ' + override_name
        property = {}
        if main_prop['type'] == Type.MATERIAL:
            property[new_name] =  MaterialParameter(main_prop['default'], self.materials[property_name].extension)
        else:
            property[new_name] = Parameter(main_prop['default'], main_prop['type'], main_prop['size'])
        self.setup(property, replace_parameters= False)
    
    def remove_override(self, property):
        rna = self.get_rna()
        if property in rna:
            rna[property]['active'] = False
            self.id_data.update_tag()

    def get_parameters(self, overrides, resources):
        if '_RNA_UI' not in self.keys():
            return {}
        rna = self.get_rna()
        parameters = {}
        for key in rna.keys():
            if '@' in key:
                continue
            if rna[key]['active'] == False:
                continue
            result_key = key
            for override in reversed(overrides):
                override_key = key + ' @ ' +  override
                if override_key in rna.keys():
                    if rna[override_key]['active']:
                        key = override_key

            if rna[key]['type'] in (Type.INT, Type.FLOAT):
                try:
                    parameters[result_key] = tuple(self[key])
                except:
                    parameters[result_key] = self[key]
            elif rna[key]['type'] == Type.BOOL:
                parameters[result_key] = bool(self.bools[key].boolean)
            elif rna[key]['type'] == Type.TEXTURE:
                texture = self.textures[key].texture
                if texture:
                    parameters[result_key] = MaltTextures.get_texture(texture)
                else:
                    parameters[result_key] = None
            elif rna[key]['type'] == Type.GRADIENT:
                #TODO: Only works for materials
                color_ramp = get_color_ramp(self.id_data, key).color_ramp
                parameters[result_key] = MaltTextures.get_gradient(color_ramp, self.id_data.name_full, key)
            elif rna[key]['type'] == Type.MATERIAL:
                material = self.materials[key].material
                extension = self.materials[key].extension
                if material:
                    materials = resources['materials']
                    material_name = material.name_full
                    if material_name not in materials.keys():
                        shader = {
                            'path': bpy.path.abspath(material.malt.shader_source, library=material.library),
                            'parameters': material.malt.parameters.get_parameters(overrides, resources)
                        }
                        material_parameters = material.malt_parameters.get_parameters(overrides, resources)
                        materials[material_name] = Scene.Material(shader, material_parameters)
                    parameters[result_key] = materials[material_name]
                else:
                    parameters[result_key] = None
        return parameters

    
    def draw_ui(self, layout, filter=None, mask=None, is_node_socket=False):
        if '_RNA_UI' not in self.keys():
            return #Can't modify ID classes from here
        rna = self.get_rna()

        import re
        def natual_sort_key(k):
            return [int(c) if c.isdigit() else c for c in re.split('([0-9]+)', k)]

        # Most drivers sort the uniforms in alphabetical order anyway, 
        # so there's no point in tracking the actual index since it doesn't follow
        # the declaration order
        keys = sorted(rna.keys(), key=natual_sort_key)

        #layout.use_property_split = True
        layout.use_property_decorate = False
        
        namespace_stack = [(None, layout)]

        #'''
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout = layout.column(align=True)
        #'''

        for key in keys:
            if rna[key]['active'] == False:
                continue
            if filter and rna[key]['filter'] and rna[key]['filter'] != filter:
                continue
            
            if mask and key not in mask:
                continue
            
            names = key.split('.')

            if len(names) == 1:
                namespace_stack = namespace_stack[:1]
                layout = namespace_stack[0][1]
            else:
                for i in range(0, len(names) - 1):
                    name = names[i]
                    stack_i = i+1
                    if len(namespace_stack) > stack_i and namespace_stack[stack_i][0] != name:
                        namespace_stack = namespace_stack[:stack_i]
                    if len(namespace_stack) < stack_i+1:
                        box = namespace_stack[stack_i - 1][1].box()
                        box.label(text=name + " :")
                        namespace_stack.append((name, box))
                    layout = namespace_stack[stack_i][1]
            
            names = [name.replace('_',' ') for name in names]

            name = names[-1]

            def make_row(label_only = False):
                if is_node_socket:
                    #c = layout.column()
                    layout.label(text=name)
                    return layout
                
                is_override = False
                label = name
                if '@' in name:
                    is_override = True
                    label = '⇲ '+name.split(' @ ')[1]
                
                row = layout.row(align=True)
                result = row.split()
                if not label_only:
                    result = result.split(factor=0.66)
                    result.alignment = 'RIGHT'
                result.label(text=label)

                if is_override:
                    delete_op = row.operator('wm.malt_delete_override', text='', icon='X')
                    delete_op.properties_path = to_json_rna_path(self)
                    delete_op.property = key
                else:
                    override_op = row.operator('wm.malt_new_override', text='', icon='DECORATE_OVERRIDE')
                    override_op.properties_path = to_json_rna_path(self)
                    override_op.property = key
                
                return result
                
            if rna[key]['type'] in (Type.INT, Type.FLOAT):
                #TODO: add subtype toggle
                make_row().prop(self, '["'+key+'"]', text='')
            elif rna[key]['type'] == Type.BOOL:
                make_row().prop(self.bools[key], 'boolean', text='')
            elif rna[key]['type'] == Type.TEXTURE:
                make_row(True)
                row = layout.row()
                if self.textures[key].texture:
                    row = row.split(factor=0.8)
                row.template_ID(self.textures[key], "texture", new="image.new", open="image.open")
                if self.textures[key].texture:
                    row.prop(self.textures[key].texture.colorspace_settings, 'name', text='')
            elif rna[key]['type'] == Type.GRADIENT:
                make_row(True)
                layout.template_color_ramp(get_color_ramp(self.id_data, key), 'color_ramp')
            elif rna[key]['type'] == Type.MATERIAL:
                make_row(True)
                row = layout.row(align=True)
                row.template_ID(self.materials[key], "material")
                material_path = to_json_rna_path(self.materials[key])
                if self.materials[key].material:
                    extension = self.materials[key].extension
                    row.operator('material.malt_add_material', text='', icon='DUPLICATE').material_path = material_path
                    material = self.materials[key].material
                    material.malt.draw_ui(layout.box(), extension, material.malt_parameters)
                else:
                    row.operator('material.malt_add_material', text='New', icon='ADD').material_path = material_path

import json

def to_json_rna_path(prop):
    blend_id = prop.id_data
    id_type = str(blend_id.__class__).split('.')[-1]
    id_name = blend_id.name_full
    path = prop.path_from_id()
    return json.dumps((id_type, id_name, path))

def from_json_rna_path(prop):
    id_type, id_name, path = json.loads(prop)
    data_map = {
        'Object' : bpy.data.objects,
        'Mesh' : bpy.data.meshes,
        'Light' : bpy.data.lights,
        'Camera' : bpy.data.cameras,
        'Material' : bpy.data.materials,
        'World': bpy.data.worlds,
        'Scene': bpy.data.scenes,
    }
    for class_name, data in data_map.items():
        if class_name in id_type:
            return data[id_name].path_resolve(path)
    return None

class OT_MaltNewMaterial(bpy.types.Operator):
    bl_idname = "material.malt_add_material"
    bl_label = "Malt Add Material"
    bl_options = {'INTERNAL'}

    material_path : bpy.props.StringProperty()

    def execute(self, context):
        material_wrapper = from_json_rna_path(self.material_path)
        if material_wrapper.material:
            material_wrapper.material = material_wrapper.material.copy()
        else:
            material_wrapper.material = bpy.data.materials.new('Material')
        material_wrapper.id_data.update_tag()
        return {'FINISHED'}

class OT_MaltNewOverride(bpy.types.Operator):
    bl_idname = "wm.malt_new_override"
    bl_label = "Malt Add A Property Override"
    bl_options = {'INTERNAL'}

    properties_path : bpy.props.StringProperty()
    property : bpy.props.StringProperty()
    
    def get_override_enums(self, context):
        overrides = context.scene.world.malt.overrides.split(',')
        result = []
        for i, override in enumerate(overrides):
            result.append((override, override, '', i))
        return result
    override : bpy.props.EnumProperty(items=get_override_enums)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "override")
    
    def execute(self, context):
        properties = from_json_rna_path(self.properties_path)
        properties.add_override(self.property, self.override)
        return {'FINISHED'}

class OT_MaltDeleteOverride(bpy.types.Operator):
    bl_idname = "wm.malt_delete_override"
    bl_label = "Malt Delete A Property Override"
    bl_options = {'INTERNAL'}

    properties_path : bpy.props.StringProperty()
    property : bpy.props.StringProperty()

    def execute(self, context):
        properties = from_json_rna_path(self.properties_path)
        properties.remove_override(self.property)
        return {'FINISHED'}

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
            self.layout.active = owner.library is None #Only local data can be edited
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

# In MaltMaterials
'''
class MALT_PT_Material(MALT_PT_Base):
    bl_context = "material"
    @classmethod
    def get_malt_property_owner(cls, context):
        if context.material:
            return context.material
'''

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
    OT_MaltNewMaterial,
    OT_MaltNewOverride,
    OT_MaltDeleteOverride,
    MALT_PT_Base,
    MALT_PT_Scene,
    MALT_PT_World,
    MALT_PT_Camera,
    MALT_PT_Object,
    MALT_PT_Mesh,
    MALT_PT_Light,
)

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


