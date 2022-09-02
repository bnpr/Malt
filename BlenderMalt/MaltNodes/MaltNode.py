from Malt.PipelineParameters import Parameter, Type
import bpy    
from BlenderMalt.MaltProperties import MaltPropertyGroup

COLUMN_TYPES = ['Texture','sampler','Material']

class MaltNode():

    malt_parameters : bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    disable_updates : bpy.props.BoolProperty(name="Disable Updates", default=False,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    first_setup : bpy.props.BoolProperty(default=True,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    subscribed : bpy.props.BoolProperty(name="Subscribed", default=False,
        options={'SKIP_SAVE','LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    malt_label : bpy.props.StringProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    #Used on copy() to find the correct node instance
    temp_id : bpy.props.StringProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    internal_name : bpy.props.StringProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def get_parameters(self, overrides, resources):
        parameters = self.id_data.malt_parameters.get_parameters(overrides, resources)
        result = {}
        for name, input in self.inputs.items():
            if '@' in name or input.active == False:
                continue
            key = input.get_source_global_reference()
            key = key.replace('"','')
            if key in parameters:
                result[name] = parameters[key]
        return result

    # Blender will trigger update callbacks even before init and update has finished
    # So we use some wrappers to get a more sane behaviour
    def _disable_updates_wrapper(self, function):
        tree = self.id_data
        initial_tree_updates = tree.disable_updates
        tree.disable_updates = True
        self.disable_updates = True
        try:
            function()
        except:
            import traceback
            traceback.print_exc()
        tree.disable_updates = initial_tree_updates
        self.disable_updates = False

    def init(self, context):
        self._disable_updates_wrapper(self.malt_init)
        
    def setup(self, context=None):
        self.setup_implementation()
    
    def setup_implementation(self, copy=None):
        self.temp_id = str(hash(self))
        if self.internal_name == '':
            label = self.malt_label if self.malt_label != '' else self.name
            self.internal_name = self.id_data.get_unique_node_id(label)
        self._disable_updates_wrapper(lambda: self.malt_setup(copy=copy))
        self.first_setup = False
        if self.subscribed == False:
            def callback(dummy=None):
                self.setup_implementation()
            bpy.msgbus.subscribe_rna(key=self.path_resolve('name', False), owner=self, args=(None,), notify=callback)
            self.subscribed = True

    def update(self):
        if self.disable_updates:
            return
        self._disable_updates_wrapper(self.malt_update)
    
    def copy(self, node):
        #Find the node from its node tree so we have access to the node id_data
        for tree in bpy.data.node_groups:
            if node.name in tree.nodes:
                if node.temp_id == tree.nodes[node.name].temp_id:
                    node = tree.nodes[node.name]
                    break
        #We can't copy a node without ID data
        if node.id_data is None:
            node = None
        self.subscribed = False #TODO: Is this needed???
        self.internal_name = ''
        self.setup_implementation(copy=node)
    
    def free(self):
        for input in self.inputs:
            key = self.get_input_parameter_name(input.name)
            self.id_data.malt_parameters.remove_property(key)
        
    def malt_init(self):
        pass

    def malt_setup(self, copy=None):
        pass
    
    def malt_update(self):
        pass

    def on_socket_update(self, socket):
        pass

    def setup_sockets(self, inputs, outputs, expand_structs=True, show_in_material_panel=False, copy=None):
        def _expand_structs(sockets):
            result = {}
            for name, dic in sockets.items():
                result[name] = dic
                struct_type = self.id_data.get_struct_type(dic['type'])
                if struct_type:
                    for member in struct_type['members']:
                        result[f"{name}.{member['name']}"] = member
            return result
        if expand_structs:
            inputs = _expand_structs(inputs)
            outputs = _expand_structs(outputs)
        def setup(current, new):
            remove = []
            for e in current.keys():
                if e not in new:
                    remove.append(current[e])
            for e in remove:
                if e.is_linked == False or self.should_delete_outdated_links():
                    current.remove(e)
                else:
                    e.active = False
            socket_index = 0
            for i, (name, dic) in enumerate(new.items()):
                if '@' in name:
                    continue #Skip overrides
                type = dic['type']
                size = dic['size'] if 'size' in dic else 0
                if name not in current:
                    current.new('MaltSocket', name)
                    current[name].show_in_material_panel = show_in_material_panel
                if isinstance(type, Parameter):
                    current[name].data_type = type.type_string()
                    current[name].array_size = 0 #TODO
                else:
                    current[name].data_type = type
                    current[name].array_size = size
                current[name].active = True
                current[name].default_initialization = ''
                try:
                    current[name].ui_label = dic['meta']['label']
                except:
                    current[name].ui_label = name
                try:
                    default = dic['meta']['default']
                    if isinstance(default, str):
                        current[name].default_initialization = default
                except:
                    pass
                if current.find(name) != socket_index:
                    current.move(current.find(name), socket_index)
                socket_index += 1

        setup(self.inputs, inputs)
        setup(self.outputs, outputs)
        parameters = {}
        for name, input in inputs.items():
            parameter = None
            type = input['type']
            size = input['size'] if 'size' in input else 0
            try:
                subtype = input['meta']['subtype']
            except:
                subtype = None
            if isinstance(type, Parameter):
                parameter = type
            else:
                default_value = input.get('meta', {}).get('default', None)
                if size == 0:
                    try:
                        parameter = Parameter.from_glsl_type(type, subtype, default_value)
                    except:
                        parameter = Parameter(type, Type.OTHER)
                else:
                    parameter = Parameter(type, Type.OTHER)
            if parameter:
                for k,v in input.get('meta', {}).items():
                    if k not in parameter.__dict__.keys():
                        parameter.__dict__[k] = v
                label = input.get('meta', {}).get('label', name)
                node_label = self.draw_label().replace('.', ' ')
                parameter.label = f'{node_label}.{label}'
                parameters[self.get_input_parameter_name(name)] = parameter
        
        copy_map = None
        copy_map = {}
        if copy is None:
            #Copy from the node parameters (backward compatibility)
            materials = [m for m in bpy.data.materials if m.malt.shader_nodes is self.id_data]
            transpiler = self.id_data.get_transpiler()
            #Rename old material parameters (backward compatibility) 
            for key in self.malt_parameters.get_rna().keys():
                new_name = self.get_input_parameter_name(key)
                if new_name in self.id_data.malt_parameters.get_rna().keys():
                    continue
                copy_map[new_name] = key
                old_name = transpiler.global_reference(transpiler.get_source_name(self.name), key)
                for material in materials:
                    if old_name in material.malt.parameters.get_rna().keys():
                        material.malt.parameters.rename_property(old_name, new_name)
            copy = self.malt_parameters
        else:
            for key in inputs.keys():
                from_name = copy.get_input_parameter_name(key)
                to_name = self.get_input_parameter_name(key)
                copy_map[to_name] = from_name
            copy = copy.id_data.malt_parameters

        self.id_data.malt_parameters.setup(parameters, skip_private=False, replace_parameters=False,
            copy_from=copy, copy_map=copy_map)
        for input in self.inputs:
            #Sync old nodes with the new system
            input.show_in_material_panel_update()
        self.setup_socket_shapes()
        if self.first_setup:
            self.setup_width()
    
    def get_input_parameter_name(self, key):
        name = key
        postfix = ''
        if ' @ ' in name:
            name_postfix = name.split(' @ ')
            name = name_postfix[0]
            postfix = ' @ ' + name_postfix[1]
        if name in self.inputs.keys() and self.inputs[name].active:
            name = self.inputs[name].get_source_global_reference()
        name += postfix 
        name = name.replace('"','')
        return name
    
    def should_delete_outdated_links(self):
        return False
    
    def calc_node_width(self, point_size, dpi) -> float:
        import blf 
        blf.size(0, point_size, dpi)
        header_padding = 36 # account for a little space for the arrow icon + extra padding on the side of a label
        socket_padding = 31 # account for little offset of the text from the node border

        def adjust_width(width, text, scale=1, padding=0):
            new_width = blf.dimensions(0, text)[0] * scale + padding
            result = max(width, new_width)
            return result

        max_width = adjust_width(0, self.draw_label(), padding=header_padding)
        for input in self.inputs.values():
            scale = 2 
            if input.default_initialization or '.' in input.name:
                scale = 1
            max_width = adjust_width(max_width, input.get_ui_label(), scale=scale, padding=socket_padding*scale)
        for output in self.outputs.values():
            max_width = adjust_width(max_width, output.get_ui_label(), padding=socket_padding)
        return max_width

    def setup_width(self):
        point_size = bpy.context.preferences.ui_styles[0].widget_label.points
        dpi = 72 #dont use bpy.context.preferences.system.dpi because that is influenced by the UI scale but the node widths are not 
        self.width = self.calc_node_width(point_size, dpi)

    def get_source_name(self):
        return self.id_data.get_transpiler().get_source_name(self.internal_name)

    def get_source_code(self, transpiler):
        if self.id_data.get_source_language() == 'GLSL':
            return '/*{} not implemented*/'.format(self)
        elif self.id_data.get_source_language() == 'Python':
            return '# {} not implemented'.format(self)

    def get_source_socket_reference(self, socket):
        if self.id_data.get_source_language() == 'GLSL':
            return '/*{} not implemented*/'.format(socket.name)
        elif self.id_data.get_source_language() == 'Python':
            return '# {} not implemented'.format(socket.name)
    
    def sockets_to_global_parameters(self, sockets, transpiler):
        code = ''
        for socket in sockets:
            if socket.active == False:
                continue
            if socket.data_type != '' and socket.get_linked() is None and socket.is_struct_member() == False:
                code += transpiler.global_declaration(socket.data_type, socket.array_size, socket.get_source_global_reference())
        return code
    
    def get_source_global_parameters(self, transpiler):
        return self.sockets_to_global_parameters(self.inputs, transpiler)
    
    def setup_socket_shapes(self):
        from itertools import chain
        for socket in chain(self.inputs.values(), self.outputs.values()):
            socket.setup_shape()
    
    def is_column_type(self, data_type):
        global COLUMN_TYPES
        for type in COLUMN_TYPES:
            if type in data_type:
                return True
        return False
    
    def draw_socket(self, context, layout, socket, text):
        draw_parameter = socket.is_output == False and socket.get_linked() is None and socket.default_initialization == ''
        if socket.is_struct_member() and (socket.get_struct_socket().get_linked() or socket.get_struct_socket().default_initialization != ''):
            draw_parameter = False
        if draw_parameter:
            column = layout.column()
            def get_layout():
                if draw_parameter and self.is_column_type(socket.data_type):
                    return column.column()
                else:
                    return column.row()
            parameter_key = socket.get_source_global_reference()
            parameter_key = parameter_key.replace('"','')
            self.id_data.malt_parameters.draw_parameter(get_layout(), parameter_key, text, is_node_socket=True)
            rna_keys = self.id_data.malt_parameters.get_rna().keys()
            for override in ('Preview', 'Final Render'):
                key = f'{parameter_key} @ {override}'
                if key in rna_keys:
                    self.id_data.malt_parameters.draw_parameter(get_layout(), key, None, is_node_socket=True)
        else:
            layout.label(text=text)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'MaltTree'
    
    def draw_label(self):
        print_label = self.malt_label != ''
        if print_label:
            for input in self.inputs:
                if input.show_in_material_panel:
                    print_label = False
                    break
        if print_label:
            return self.malt_label
        else:
            return self.name.replace('_', ' ')

    
classes = []

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

