# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import os
import bpy
from Malt.Parameter import Type, Parameter, MaterialParameter
from Malt import Scene
from . import MaltTextures

class MaltBoolPropertyWrapper(bpy.types.PropertyGroup):
    boolean : bpy.props.BoolProperty()

# WORKAROUND: We can't declare color ramps from python,
# so we use the ones stored inside textures
class MaltGradientPropertyWrapper(bpy.types.PropertyGroup):
    def poll(self, texture):
        return texture.type == 'BLEND' and texture.use_color_ramp
    texture : bpy.props.PointerProperty(type=bpy.types.Texture, poll=poll)

class MaltTexturePropertyWrapper(bpy.types.PropertyGroup):
    texture : bpy.props.PointerProperty(type=bpy.types.Image)

class MaltMaterialPropertyWrapper(bpy.types.PropertyGroup):
    #TODO:poll
    material : bpy.props.PointerProperty(type=bpy.types.Material)
    extension : bpy.props.StringProperty()

class MaltGraphPropertyWrapper(bpy.types.PropertyGroup):
    def poll(self, tree):
        return tree.bl_idname == 'MaltTree' and tree.graph_type == self.type
    graph : bpy.props.PointerProperty(type=bpy.types.NodeTree, poll=poll)
    type : bpy.props.StringProperty()

class MaltPropertyGroup(bpy.types.PropertyGroup):

    bools : bpy.props.CollectionProperty(type=MaltBoolPropertyWrapper)
    gradients : bpy.props.CollectionProperty(type=MaltGradientPropertyWrapper)    
    textures : bpy.props.CollectionProperty(type=MaltTexturePropertyWrapper)    
    materials : bpy.props.CollectionProperty(type=MaltMaterialPropertyWrapper)
    graphs : bpy.props.CollectionProperty(type=MaltGraphPropertyWrapper)

    parent : bpy.props.PointerProperty(type=bpy.types.ID, name="Override From")
    override_from_parents : bpy.props.CollectionProperty(type=MaltBoolPropertyWrapper)

    def get_rna(self):
        try:
            if '_RNA_UI' not in self.keys():
                self['_RNA_UI'] = {}
            return self['_RNA_UI']
        except:
            return {}

    def setup(self, parameters, replace_parameters=True, reset_to_defaults=False, skip_private=True):
        rna = self.get_rna()
        
        def setup_parameter(name, parameter):
            if name not in rna.keys():
                rna[name] = {}

            type_changed = 'type' not in rna[name].keys() or rna[name]['type'] != parameter.type
            size_changed = 'size' in rna[name].keys() and rna[name]['size'] != parameter.size

            if reset_to_defaults:
                #TODO: Rename
                type_changed = True

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
                if type_changed or self.textures[name] == rna[name]['default']:
                    if isinstance(parameter.default_value, bpy.types.Image):
                        self.textures.texture = parameter.default_value

            if parameter.type == Type.GRADIENT:
                if name not in self.gradients:
                    self.gradients.add().name = name
                    # Load gradient from material nodes (backward compatibility)
                    if isinstance(self.id_data, bpy.types.Material):
                        material = self.id_data
                        if material.use_nodes and name in material.node_tree.nodes:
                            self.gradients[name].texture = bpy.data.textures.new('malt_color_ramp', 'BLEND')
                            self.gradients[name].texture.use_color_ramp = True
                            old = material.node_tree.nodes[name].color_ramp
                            new = self.gradients[name].texture.color_ramp
                            MaltTextures.copy_color_ramp(old, new)
                            self.gradients[name].texture.update_tag()
                if type_changed or self.gradients[name] == rna[name]['default']:
                    if isinstance(parameter.default_value, bpy.types.Texture):
                        self.gradients.texture = parameter.default_value

            if parameter.type == Type.MATERIAL:
                if name not in self.materials:
                    self.materials.add().name = name
                
                self.materials[name].extension = parameter.extension
                shader_path = parameter.default_value
                if shader_path and shader_path != '':
                    material_name = name + ' : ' + os.path.basename(shader_path)
                    if material_name not in bpy.data.materials:
                        bpy.data.materials.new(material_name)
                        material = bpy.data.materials[material_name]
                        material.malt.shader_source = shader_path    
                
                    material = self.materials[name].material
                    if type_changed or (material and rna[name]['default'] == material.malt.shader_source):
                        self.materials[name].material = bpy.data.materials[material_name]
            
            if parameter.type == Type.GRAPH:
                if name not in self.graphs:
                    self.graphs.add().name = name                
                self.graphs[name].type = parameter.default_value

            if name not in self.override_from_parents:
                self.override_from_parents.add().name = name

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
            if skip_private and (name.isupper() or name.startswith('_')):
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
            if rna[key]['active'] == False:
                continue
            #TODO: for now we assume we want floats as colors
            # ideally it should be opt-in in the UI,
            # so we can give them propper min/max values
            if rna[key]['type'] == Type.FLOAT and rna[key]['size'] >= 3:
                rna[key]['subtype'] = 'COLOR'
                rna[key]['use_soft_limits'] = True
                rna[key]['soft_min'] = 0.0
                rna[key]['soft_max'] = 1.0
            else:
                rna[key]['subtype'] = 'BLEND'
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
            parameters[key] = self.get_parameter(key, overrides, resources)
        return parameters
    
    def get_parameter(self, key, overrides, resources):
        from BlenderMalt.MaltNodes import MaltTree, MaltNode
        if self.parent and self.override_from_parents[key].boolean == False:
            try:
                return self.parent.malt_parameters.get_parameter(key, overrides, resources)
            except:
                pass
        if key not in self.get_rna().keys():
            if isinstance(self.id_data, MaltTree) and self.id_data.malt_parameters.as_pointer() == self.as_pointer():
                for node in self.id_data.nodes:
                    if isinstance(node, MaltNode):
                        for input in node.inputs:
                            if key == input.get_source_global_reference():
                                try:
                                    return node.malt_parameters.get_parameter(input.name, overrides, resources)
                                except:
                                    pass
            raise Exception()

        rna = self.get_rna()
        for override in reversed(overrides):
            override_key = key + ' @ ' +  override
            if override_key in rna.keys():
                if rna[override_key]['active']:
                    key = override_key
        if rna[key]['active'] == False:
            raise Exception()

        if rna[key]['type'] in (Type.INT, Type.FLOAT):
            try:
                return tuple(self[key])
            except:
                return self[key]
        elif rna[key]['type'] == Type.BOOL:
            return bool(self.bools[key].boolean)
        elif rna[key]['type'] == Type.TEXTURE:
            texture = self.textures[key].texture
            if texture:
                return MaltTextures.get_texture(texture)
            else:
                return None
        elif rna[key]['type'] == Type.GRADIENT:
            texture = self.gradients[key].texture
            if texture:
                return MaltTextures.get_gradient(texture)
            else:
                return None
        elif rna[key]['type'] == Type.MATERIAL:
            material = self.materials[key].material
            extension = self.materials[key].extension
            if material:
                materials = resources['materials']
                material_name = material.name_full
                if material_name not in materials.keys():
                    shader = {
                        'path': material.malt.get_source_path(),
                        'parameters': material.malt.parameters.get_parameters(overrides, resources)
                    }
                    material_parameters = material.malt_parameters.get_parameters(overrides, resources)
                    materials[material_name] = Scene.Material(shader, material_parameters)
                return materials[material_name]
            else:
                return None
        elif rna[key]['type'] == Type.GRAPH:
            graph = self.graphs[key].graph
            type = self.graphs[key].type
            if graph:
                result = {}
                result['source'] = graph.get_generated_source()
                result['parameters'] = {}
                for node in graph.nodes:
                    result['parameters'][node.get_source_name()] = node.malt_parameters.get_parameters(overrides, resources)
                return result
            else:
                return None

    
    def draw_ui(self, layout, filter=None):
        layout.use_property_decorate = False
        #layout.prop(self, "parent")

        if '_RNA_UI' not in self.keys():
            return #Can't modify ID classes from here
        rna = self.get_rna()

        namespace_stack = [(None, layout)]
        
        # Most drivers sort the uniforms in alphabetical order anyway, 
        # so there's no point in tracking the actual index since it doesn't follow
        # the declaration order
        import re
        def natual_sort_key(k):
            return [int(c) if c.isdigit() else c for c in re.split('([0-9]+)', k)]
        keys = sorted(rna.keys(), key=natual_sort_key)
        
        for key in keys:
            if rna[key]['active'] == False:
                continue

            if filter and rna[key]['filter'] and rna[key]['filter'] != filter:
                continue

            names = key.replace('_0_','.').replace('_',' ').split('.')
            names = [name for name in names if name.isupper() == False]
            name = names[-1]

            #defer layout (box) creation until a property is actually drawn
            def get_layout():
                nonlocal namespace_stack
                layout = None
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
                return layout.column()

            def draw_callback(layout, property_group):
                is_self = self.as_pointer() == property_group.as_pointer()
                if self.parent and (is_self == False or self.override_from_parents[key].boolean == True):
                    layout.prop(self.override_from_parents[key], 'boolean', text='')
                if is_self == False:
                    layout.active = False
            
            self.draw_parameter(get_layout, key, name, draw_callback=draw_callback)


    def draw_parameter(self, layout, key, label, draw_callback=None, is_node_socket=False):
        from BlenderMalt.MaltNodes import MaltTree, MaltNode
        if self.parent and self.override_from_parents[key].boolean == False:
            if self.parent.malt_parameters.draw_parameter(layout, key, label, draw_callback, is_node_socket):
                return True
        if key not in self.get_rna().keys():
            if isinstance(self.id_data, MaltTree) and self.id_data.malt_parameters.as_pointer() == self.as_pointer():
                for node in self.id_data.nodes:
                    if isinstance(node, MaltNode):
                        for input in node.inputs:
                            if key == input.get_source_global_reference():
                                if input.show_in_material_panel:
                                    node.malt_parameters.draw_parameter(layout, input.name, label, draw_callback, is_node_socket=True)
                                return True
            return False
        if self.get_rna()[key]['active'] == False:
            return False
        
        try:
            layout = layout()
        except:
            #not a callback
            pass

        def make_row(label_only = False):
            nonlocal label
            if label is None:
                return layout
            is_override = False
            if '@' in label:
                is_override = True
                label = '⇲ '+label.split(' @ ')[1]
            
            row = layout.row(align=True)
            result = row.split()
            if not label_only:
                result = result.split(factor=0.66)
                result.alignment = 'RIGHT'
            result.label(text=label)
            
            if is_node_socket == False:            
                if is_override:
                    delete_op = row.operator('wm.malt_delete_override', text='', icon='X')
                    delete_op.properties_path = to_json_rna_path(self)
                    delete_op.property = key
                else:
                    override_op = row.operator('wm.malt_new_override', text='', icon='DECORATE_OVERRIDE')
                    override_op.properties_path = to_json_rna_path(self)
                    override_op.property = key
            
            if draw_callback:
                draw_callback(row, self)
            
            return result

        rna = self.get_rna()
        if rna[key]['type'] in (Type.INT, Type.FLOAT):
            #TODO: add subtype toggle
            make_row().prop(self, '["{}"]'.format(key), text='')
        elif rna[key]['type'] == Type.BOOL:
            make_row().prop(self.bools[key], 'boolean', text='')
        elif rna[key]['type'] == Type.TEXTURE:
            make_row(True)
            row = layout.row(align=True)
            if self.textures[key].texture:
                row = row.split(factor=0.8, align=True)
            row.template_ID(self.textures[key], "texture", new="image.new", open="image.open")
            if self.textures[key].texture:
                row.prop(self.textures[key].texture.colorspace_settings, 'name', text='')
        elif rna[key]['type'] == Type.GRADIENT:
            make_row(True)
            column = layout.column()
            row = column.row(align=True)
            row.template_ID(self.gradients[key], "texture")
            try:
                texture_path = to_json_rna_path(self.gradients[key])
            except:
                texture_path = to_json_rna_path_node_workaround(self, 'malt_parameters.gradients["{}"]'.format(key))
            if self.gradients[key].texture:
                row.operator('texture.malt_add_gradient', text='', icon='DUPLICATE').texture_path = texture_path
                column.template_color_ramp(self.gradients[key].texture, 'color_ramp')
            else:
                row.operator('texture.malt_add_gradient', text='New', icon='ADD').texture_path = texture_path
        elif rna[key]['type'] == Type.MATERIAL:
            make_row(True)
            row = layout.row(align=True)
            row.template_ID(self.materials[key], "material")
            try:
                material_path = to_json_rna_path(self.materials[key])
            except:
                material_path = to_json_rna_path_node_workaround(self, 'malt_parameters.materials["{}"]'.format(key))
            if self.materials[key].material:
                extension = self.materials[key].extension
                row.operator('material.malt_add_material', text='', icon='DUPLICATE').material_path = material_path
                material = self.materials[key].material
                material.malt.draw_ui(layout.box(), extension, material.malt_parameters)
            else:
                row.operator('material.malt_add_material', text='New', icon='ADD').material_path = material_path
        elif rna[key]['type'] == Type.GRAPH:
            make_row(True)
            row = layout.row(align=True)
            row.template_ID(self.graphs[key], "graph")
            
        return True

import json

# https://developer.blender.org/T51096
def to_json_rna_path_node_workaround(malt_property_group, path_from_group):
    tree = malt_property_group.id_data
    assert(isinstance(tree, bpy.types.NodeTree))
    for node in tree.nodes:
        if node.malt_parameters.as_pointer() == malt_property_group.as_pointer():
            path = 'nodes["{}"].{}'.format(node.name, path_from_group)
            return json.dumps(('NodeTree', tree.name_full, path))

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
        'NodeTree' : bpy.data.node_groups
    }
    for class_name, data in data_map.items():
        if class_name in id_type:
            return data[id_name].path_resolve(path)
    return None

class OT_MaltNewGradient(bpy.types.Operator):
    bl_idname = "texture.malt_add_gradient"
    bl_label = "Malt Add Gradient"
    bl_options = {'INTERNAL'}

    texture_path : bpy.props.StringProperty()

    def execute(self, context):
        gradient_wrapper = from_json_rna_path(self.texture_path)
        if gradient_wrapper.texture:
            gradient_wrapper.texture = gradient_wrapper.texture.copy()
        else:
            texture = bpy.data.textures.new('malt_color_ramp', 'BLEND')
            texture.use_color_ramp = True
            texture.color_ramp.elements[0].alpha = 1.0
            gradient_wrapper.texture = texture
        gradient_wrapper.id_data.update_tag()
        gradient_wrapper.texture.update_tag()
        from . MaltTextures import add_gradient_workaround
        add_gradient_workaround(gradient_wrapper.texture)
        return {'FINISHED'}

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
        material_wrapper.material.update_tag()
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
        properties.id_data.update_tag()
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
        properties.id_data.update_tag()
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
        if context.object and context.object.data and context.object.type in ('MESH', 'CURVE', 'SURFACE', 'META', 'FONT'):
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
    MaltBoolPropertyWrapper,
    MaltGradientPropertyWrapper,
    MaltTexturePropertyWrapper,
    MaltMaterialPropertyWrapper,
    MaltGraphPropertyWrapper,
    MaltPropertyGroup,
    OT_MaltNewGradient,
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
    bpy.types.MetaBall.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup)
    bpy.types.Light.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup)


def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

    del bpy.types.Scene.malt_parameters
    del bpy.types.World.malt_parameters
    del bpy.types.Camera.malt_parameters
    del bpy.types.Object.malt_parameters
    del bpy.types.Material.malt_parameters
    del bpy.types.Mesh.malt_parameters
    del bpy.types.Curve.malt_parameters
    del bpy.types.Light.malt_parameters


