import os
import bpy
from Malt.PipelineParameters import Type, Parameter, MaterialParameter
from Malt import Scene
from . import MaltTextures

class MaltBoolPropertyWrapper(bpy.types.PropertyGroup):
    boolean : bpy.props.BoolProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

class MaltEnumPropertyWrapper(bpy.types.PropertyGroup):
    enum_options : bpy.props.StringProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    def get_items(self, context=None):
        for option in self.enum_options.split(','):
            yield (option, option, option)
    
    enum : bpy.props.EnumProperty(items=get_items, name='',
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

# WORKAROUND: We can't declare color ramps from python,
# so we use the ones stored inside textures
class MaltGradientPropertyWrapper(bpy.types.PropertyGroup):
    def poll(self, texture):
        return texture.type == 'BLEND' and texture.use_color_ramp
    texture : bpy.props.PointerProperty(type=bpy.types.Texture, poll=poll,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def add_or_duplicate(self):
        if self.texture:
            self.texture = self.texture.copy()
        else:
            texture = bpy.data.textures.new('malt_color_ramp', 'BLEND')
            texture.use_color_ramp = True
            texture.color_ramp.elements[0].alpha = 1.0
            self.texture = texture
        self.id_data.update_tag()
        self.texture.update_tag()
        from . MaltTextures import add_gradient_workaround
        add_gradient_workaround(self.texture)

class MaltTexturePropertyWrapper(bpy.types.PropertyGroup):
    texture : bpy.props.PointerProperty(type=bpy.types.Image,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

class MaltMaterialPropertyWrapper(bpy.types.PropertyGroup):
    #TODO:poll
    material : bpy.props.PointerProperty(type=bpy.types.Material,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    extension : bpy.props.StringProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def add_or_duplicate(self):
        if self.material:
            self.material = self.material.copy()
        else:
            self.material = bpy.data.materials.new('Material')
        self.id_data.update_tag()
        self.material.update_tag()

class MaltGraphPropertyWrapper(bpy.types.PropertyGroup):
    def poll(self, tree):
        return tree.bl_idname == 'MaltTree' and tree.graph_type == self.type
    graph : bpy.props.PointerProperty(type=bpy.types.NodeTree, poll=poll,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    type : bpy.props.StringProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def add_or_duplicate(self):
        if self.graph:
            self.graph = self.graph.copy()
        else:
            self.graph = bpy.data.node_groups.new(f'{self.type} Node Tree', 'MaltTree')
            self.graph.graph_type = self.type
        self.id_data.update_tag()
        self.graph.update_tag()

class MaltPropertyGroup(bpy.types.PropertyGroup):

    bools : bpy.props.CollectionProperty(type=MaltBoolPropertyWrapper,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'})
    enums : bpy.props.CollectionProperty(type=MaltEnumPropertyWrapper,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'})
    gradients : bpy.props.CollectionProperty(type=MaltGradientPropertyWrapper,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'})    
    textures : bpy.props.CollectionProperty(type=MaltTexturePropertyWrapper,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'})    
    materials : bpy.props.CollectionProperty(type=MaltMaterialPropertyWrapper,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'})
    graphs : bpy.props.CollectionProperty(type=MaltGraphPropertyWrapper,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'})

    parent : bpy.props.PointerProperty(type=bpy.types.ID, name="Override From",
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    override_from_parents : bpy.props.CollectionProperty(type=MaltBoolPropertyWrapper,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'})

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

            if self.parent:
                try:
                    rna_copy = {}
                    parameter.default_value = self.parent.malt_parameters.get_parameter(name, [], {},
                        retrieve_blender_type=True, rna_copy=rna_copy)
                    parameter.default_value = rna_copy.get("default", None)
                    parameter.type = rna_copy.get('type', None)
                    parameter.subtype = rna_copy.get('malt_subtype', None)
                    parameter.size = rna_copy.get('size', None)
                    parameter.filter = rna_copy.get('filter', None)
                    parameter.label = rna_copy.get('label', None)
                    parameter.enum_options = rna_copy.get('enum_options', None)
                except:
                    pass

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
            
            if parameter.type == Type.STRING:
                if type_changed or equals(rna[name]['default'], self[name]):
                    self[name] = parameter.default_value   

            if parameter.type == Type.BOOL:
                if name not in self.bools:
                    self.bools.add().name = name
                if type_changed or equals(rna[name]['default'], self.bools[name].boolean):
                    self.bools[name].boolean = parameter.default_value
                elif size_changed:
                    resize()
            
            if parameter.type == Type.ENUM:
                if name not in self.enums:
                    self.enums.add().name = name
                rna[name]['enum_options'] = parameter.enum_options
                self.enums[name].enum_options = ','.join(parameter.enum_options)
                if type_changed or equals(rna[name]['default'], self.enums[name].enum):
                    self.enums[name].enum = parameter.default_value
            
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
                    if isinstance(shader_path, str):
                        material_name = name + ' : ' + os.path.basename(shader_path)
                        if material_name not in bpy.data.materials:
                            bpy.data.materials.new(material_name)
                            material = bpy.data.materials[material_name]
                            material.malt.shader_source = shader_path
                        material = self.materials[name].material
                        if type_changed or (material and rna[name]['default'] == material.malt.shader_source):
                            self.materials[name].material = bpy.data.materials[material_name]
                    
                    if isinstance(shader_path, tuple):
                        blend_path, material_name = parameter.default_value
                        blend_path += '.blend'
                        if material_name not in bpy.data.materials:
                            internal_dir = 'Material'
                            bpy.ops.wm.append(
                                filepath=os.path.join(blend_path, internal_dir, material_name),
                                directory=os.path.join(blend_path, internal_dir),
                                filename=material_name
                            )    
                        if type_changed:
                            self.materials[name].material = bpy.data.materials[material_name]
                    
            if parameter.type == Type.GRAPH:
                if name not in self.graphs:
                    self.graphs.add().name = name
                self.graphs[name].type = parameter.graph_type
                if parameter.default_value and isinstance(parameter.default_value, tuple):
                    blend_path, tree_name = parameter.default_value
                    blend_path += '.blend'
                    if tree_name not in bpy.data.node_groups:
                        internal_dir = 'NodeTree'
                        bpy.ops.wm.append(
                            filepath=os.path.join(blend_path, internal_dir, tree_name),
                            directory=os.path.join(blend_path, internal_dir),
                            filename=tree_name
                        )
                    if type_changed:
                        self.graphs[name].graph = bpy.data.node_groups[tree_name]
                    if self.graphs[name].graph is not None:
                        assert(parameter.graph_type == self.graphs[name].graph.graph_type)

            if name not in self.override_from_parents:
                self.override_from_parents.add().name = name

            rna[name]['active'] = True
            rna[name]["default"] = parameter.default_value
            rna[name]['type'] = parameter.type
            rna[name]['malt_subtype'] = parameter.subtype
            rna[name]['size'] = parameter.size
            rna[name]['filter'] = parameter.filter

            rna[name]['min'] = getattr(parameter, 'min', None)
            rna[name]['max'] = getattr(parameter, 'max', None)
            
            if hasattr(parameter, 'label'):
                rna[name]['label'] = parameter.label
            else:
                rna[name]['label'] = name.replace('_',' ').replace('_0_','.').title()
            

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
                    if rna[key]['type'] != rna[main_name]['type'] or rna[key]['size'] != rna[main_name]['size']:
                        parameter = Parameter(rna[main_name]['default'], rna[main_name]['type'],
                            rna[main_name]['size'], rna[main_name]['filter'], rna[main_name]['malt_subtype'])
                        setup_parameter(key, parameter)
        
        for key, value in rna.items():
            rna_prop = rna[key]
            if rna_prop['active'] == False:
                continue
            #Default to color since it's the most common use case
            malt_subtype = rna_prop.get('malt_subtype')
            if rna_prop['type'] == Type.FLOAT and rna_prop['size'] >= 3 and (malt_subtype is None or malt_subtype == 'Color'):
                rna_prop['subtype'] = 'COLOR'
                rna_prop['use_soft_limits'] = True
                rna_prop['soft_min'] = 0.0
                rna_prop['soft_max'] = 1.0
            else:
                rna_prop['subtype'] = 'BLEND'
                rna_prop['use_soft_limits'] = False
            
            if bpy.app.version[0] >= 3:
                if rna_prop['type'] in (Type.FLOAT, Type.INT):
                    ui = self.id_properties_ui(key)
                    if rna_prop['subtype'] == 'COLOR':
                        ui.update(default=rna_prop['default'], subtype='COLOR', soft_min = 0.0, soft_max = 1.0)
                    elif rna_prop['min'] is not None and rna_prop['max'] is not None:
                        ui.update(default=rna_prop['default'], subtype='NONE', 
                            soft_min = rna_prop['min'], soft_max = rna_prop['max'])
                    else:
                        ui.update(default=rna_prop['default'], subtype='NONE')

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
            property[new_name] = Parameter(main_prop['default'], main_prop['type'], main_prop['size'], main_prop['filter'], main_prop['malt_subtype'])
        self.setup(property, replace_parameters= False)
    
    def remove_override(self, property):
        rna = self.get_rna()
        if property in rna:
            rna[property]['active'] = False
            self.id_data.update_tag()

    def get_parameters(self, overrides, proxys):
        if '_RNA_UI' not in self.keys():
            return {}
        rna = self.get_rna()
        parameters = {}
        for key in rna.keys():
            if '@' in key:
                continue
            if rna[key]['active'] == False:
                continue
            parameters[key] = self.get_parameter(key, overrides, proxys)
        return parameters
    
    def get_parameter(self, key, overrides, proxys, retrieve_blender_type=False, rna_copy={}):
        from . MaltNodes.MaltNodeTree import MaltTree
        from . MaltNodes.MaltNode import MaltNode
        if self.parent and self.override_from_parents[key].boolean == False:
            try:
                return self.parent.malt_parameters.get_parameter(key, overrides, proxys, retrieve_blender_type, rna_copy)
            except:
                pass
        if key not in self.get_rna().keys():
            if isinstance(self.id_data, MaltTree) and self.id_data.malt_parameters.as_pointer() == self.as_pointer():
                if self.id_data.is_active():
                    for node in self.id_data.nodes:
                        if isinstance(node, MaltNode):
                            for input in node.inputs:
                                if key == input.get_source_global_reference():
                                    try:
                                        return node.malt_parameters.get_parameter(input.name, overrides, proxys, 
                                            retrieve_blender_type, rna_copy)
                                    except:
                                        pass
            raise Exception()

        rna = self.get_rna()
        rna_copy.update(rna[key])
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
        elif rna[key]['type'] == Type.STRING:
            return self[key]
        elif rna[key]['type'] == Type.BOOL:
            return bool(self.bools[key].boolean)
        elif rna[key]['type'] == Type.ENUM:
            return self.enums[key].enum_options.split(',').index(self.enums[key].enum)
        elif rna[key]['type'] == Type.TEXTURE:
            texture = self.textures[key].texture
            if retrieve_blender_type:
                return texture
            if texture:
                texture_key = ('texture', texture.name_full)
                if texture_key not in proxys.keys():
                    proxys[texture_key] = MaltTextures.get_texture(texture)
                return proxys[texture_key]
            else:
                return None
        elif rna[key]['type'] == Type.GRADIENT:
            texture = self.gradients[key].texture
            if retrieve_blender_type:
                return texture
            if texture:
                gradient_key = ('gradient', texture.name_full)
                if gradient_key not in proxys.keys():
                    proxys[gradient_key] = MaltTextures.get_gradient(texture)
                return proxys[gradient_key]
            else:
                return None
        elif rna[key]['type'] == Type.MATERIAL:
            material = self.materials[key].material
            extension = self.materials[key].extension
            if retrieve_blender_type:
                return material
            if material:
                material_key = ('material', material.name_full)
                if material_key not in proxys.keys():
                    path = material.malt.get_source_path()
                    shader_parameters = material.malt.parameters.get_parameters(overrides, proxys)
                    material_parameters = material.malt_parameters.get_parameters(overrides, proxys)
                    from Bridge.Proxys import MaterialProxy
                    proxys[material_key] = MaterialProxy(path, shader_parameters, material_parameters)
                return proxys[material_key]
            else:
                return None
        elif rna[key]['type'] == Type.GRAPH:
            graph = self.graphs[key].graph
            type = self.graphs[key].type
            if retrieve_blender_type:
                return graph
            if graph and graph.is_active():
                result = {}
                result['source'] = graph.get_generated_source()
                result['parameters'] = {}
                for node in graph.nodes:
                    if isinstance(node, MaltNode):
                        result['parameters'][node.get_source_name()] = node.get_parameters(overrides, proxys)
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
            
            labels = rna[key].get('label', key.replace('_0_','.').replace('_',' '))
            labels = labels.split('.')
            label = labels[-1]
            
            #defer layout (box) creation until a property is actually drawn
            def get_layout():
                nonlocal namespace_stack
                layout = None
                if len(labels) == 1:
                    namespace_stack = namespace_stack[:1]
                    layout = namespace_stack[0][1]
                else:
                    for i in range(0, len(labels) - 1):
                        label = labels[i]
                        stack_i = i+1
                        if len(namespace_stack) > stack_i and namespace_stack[stack_i][0] != label:
                            namespace_stack = namespace_stack[:stack_i]
                        if len(namespace_stack) < stack_i+1:
                            box = namespace_stack[stack_i - 1][1].box()
                            box.label(text=label + " :")
                            namespace_stack.append((label, box))
                        layout = namespace_stack[stack_i][1]
                return layout.column()

            def draw_callback(layout, property_group):
                is_self = self.as_pointer() == property_group.as_pointer()
                if self.parent and (is_self == False or self.override_from_parents[key].boolean == True):
                    layout.prop(self.override_from_parents[key], 'boolean', text='')
                if is_self == False:
                    layout.active = False
            
            self.draw_parameter(get_layout, key, label, draw_callback=draw_callback)


    def draw_parameter(self, layout, key, label, draw_callback=None, is_node_socket=False):
        from . MaltNodes.MaltNodeTree import MaltTree
        from . MaltNodes.MaltNode import MaltNode
        if self.parent and self.override_from_parents[key].boolean == False:
            if self.parent.malt_parameters.draw_parameter(layout, key, label, draw_callback, is_node_socket):
                return True
        if key not in self.get_rna().keys():
            if isinstance(self.id_data, MaltTree) and self.id_data.malt_parameters.as_pointer() == self.as_pointer():
                if self.id_data.is_active():
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
        
        if callable(layout):
            layout = layout()

        def make_row(label_only = False):
            result = layout
            nonlocal label
            row = layout.row(align=True)
            result = row.split()
            is_override = '@' in key
            
            if is_override:
                if label is None:
                    label = key
                label = '⇲ '+label.split(' @ ')[-1]
            
            if label is not None:
                if label_only == False and is_node_socket == False:          
                    result = result.split(factor=0.66)
                    result.alignment = 'RIGHT'
                result.label(text=label)
            
            if is_override:
                row.operator('wm.malt_callback', text='', icon='X').callback.set(
                    lambda : self.remove_override(key), 'Remove Override')
            else:
                row.operator('wm.malt_new_override', text='', icon='DECORATE_OVERRIDE').callback.set(
                    lambda override_name: self.add_override(key, override_name))
            
            if draw_callback:
                draw_callback(row, self)
            
            return result

        rna = self.get_rna()
        if rna[key]['type'] in (Type.INT, Type.FLOAT, Type.STRING):
            #TODO: add subtype toggle
            slider = rna[key]['malt_subtype'] == 'Slider'
            make_row().prop(self, '["{}"]'.format(key), text='', slider=slider)
        elif rna[key]['type'] == Type.BOOL:
            make_row().prop(self.bools[key], 'boolean', text='')
        elif rna[key]['type'] == Type.ENUM:
            make_row().prop(self.enums[key], 'enum', text='')
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
            if self.gradients[key].texture:
                row.operator('wm.malt_callback', text='', icon='DUPLICATE').callback.set(
                    self.gradients[key].add_or_duplicate, 'Duplicate')
                column.template_color_ramp(self.gradients[key].texture, 'color_ramp')
            else:
                row.operator('wm.malt_callback', text='New', icon='ADD').callback.set(
                    self.gradients[key].add_or_duplicate, 'New')
        elif rna[key]['type'] == Type.MATERIAL:
            make_row(True)
            row = layout.row(align=True)
            row.template_ID(self.materials[key], "material")
            if self.materials[key].material:
                extension = self.materials[key].extension
                row.operator('wm.malt_callback', text='', icon='DUPLICATE').callback.set(
                    self.materials[key].add_or_duplicate, 'Duplicate')
                material = self.materials[key].material
                material.malt.draw_ui(layout.box(), extension, material.malt_parameters)
            else:
                row.operator('wm.malt_callback', text='New', icon='ADD').callback.set(
                    self.materials[key].add_or_duplicate, 'New')
        elif rna[key]['type'] == Type.GRAPH:
            make_row(True)
            row = layout.row(align=True)
            row.template_ID(self.graphs[key], "graph")
            if self.graphs[key].graph:
                row.operator('wm.malt_callback', text='', icon='DUPLICATE').callback.set(
                    self.graphs[key].add_or_duplicate, 'Duplicate')
                from BlenderMalt.MaltNodes.MaltNodeTree import set_node_tree
                node = self.id_data if isinstance(self.id_data, bpy.types.Node) else None
                row.operator('wm.malt_callback', text = '', icon = 'GREASEPENCIL').callback.set(
                    lambda: set_node_tree(bpy.context, self.graphs[key].graph, node)
                )
            else:
                row.operator('wm.malt_callback', text='New', icon='ADD').callback.set(
                    self.graphs[key].add_or_duplicate, 'New')
        else:
            make_row(True)
            
        return True


from . import MaltUtils

class OT_MaltNewOverride(bpy.types.Operator):
    bl_idname = "wm.malt_new_override"
    bl_label = "Malt Add A Property Override"
    bl_options = {'INTERNAL'}

    def get_override_enums(self, context):
        overrides = context.scene.world.malt.overrides.split(',')
        result = []
        for i, override in enumerate(overrides):
            result.append((override, override, '', i))
        return result
    override : bpy.props.EnumProperty(items=get_override_enums,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    callback : bpy.props.PointerProperty(type=MaltUtils.MaltCallback,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "override")
    
    def execute(self, context):
        self.callback.call(self.override)
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
    def get_parameter_type(cls):
        return None

    @classmethod
    def poll(cls, context):
        if context.scene.render.engine == 'MALT' and cls.get_malt_property_owner(context):
            from BlenderMalt.MaltPipeline import get_bridge
            bridge = get_bridge()
            parameter_type = cls.get_parameter_type()
            if bridge is None or parameter_type is None or len(getattr(bridge.parameters, parameter_type)) > 0:
                return True
        return False
    
    def draw(self, context):
        owner = self.__class__.get_malt_property_owner(context)
        if owner:
            self.layout.active = owner.library is None #Only local data can be edited
            owner.malt_parameters.draw_ui(self.layout)


class MALT_PT_Scene(MALT_PT_Base):
    bl_context = "scene"
    @classmethod
    def get_parameter_type(cls):
        return 'scene'
    @classmethod
    def get_malt_property_owner(cls, context):
        return context.scene

class MALT_PT_World(MALT_PT_Base):
    bl_context = "world"
    @classmethod
    def get_parameter_type(cls):
        return 'world'
    @classmethod
    def get_malt_property_owner(cls, context):
        return context.scene.world

class MALT_PT_Camera(MALT_PT_Base):
    bl_context = "data"
    @classmethod
    def get_parameter_type(cls):
        return 'camera'
    @classmethod
    def get_malt_property_owner(cls, context):
        if context.object.type == 'CAMERA':
            return context.object.data
        else:
            return None

class MALT_PT_Object(MALT_PT_Base):
    bl_context = "object"
    @classmethod
    def get_parameter_type(cls):
        return 'object'
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
    def get_parameter_type(cls):
        return 'mesh'
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
    MaltEnumPropertyWrapper,
    MaltGradientPropertyWrapper,
    MaltTexturePropertyWrapper,
    MaltMaterialPropertyWrapper,
    MaltGraphPropertyWrapper,
    MaltPropertyGroup,
    OT_MaltNewOverride,
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

    bpy.types.Scene.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.World.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Camera.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Object.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Material.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Mesh.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Curve.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.MetaBall.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Light.malt_parameters = bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})


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


