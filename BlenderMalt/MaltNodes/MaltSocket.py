import bpy

__TYPE_COLORS = {
    'bool': (0.8, 0.65, 0.84, 1.0),
    'Bool': (0.8, 0.65, 0.84, 1.0),
    'float': (0.63, 0.63, 0.63, 1.0),
    'Float': (0.63, 0.63, 0.63, 1.0),
    'int': (0.33, 0.55, 0.36, 1.0),
    'Int': (0.33, 0.55, 0.36, 1.0),

    'vec2': (0.39, 0.74, 0.78, 1.0),
    'vec3': (0.39, 0.39, 0.78, 1.0),
    'vec4': (0.60, 0.39, 0.78, 1.0),
    'mat4': (0.78, 0.39, 0.58, 1.0),

    'sampler1D': (0.78, 0.78, 0.46, 1.0),
    'sampler2D': (0.78, 0.64, 0.16, 1.0),
    'Texture': (0.78, 0.64, 0.16, 1.0),

    'Scene': (1.0, 1.0, 1.0, 1.0),
}
def get_type_color(type):
    if type not in __TYPE_COLORS:
        import random, hashlib
        seed = hashlib.sha1(type.encode('ascii')).digest()
        rand = random.Random(seed)
        __TYPE_COLORS[type] = (rand.random(),rand.random(),rand.random(),1.0)
    return __TYPE_COLORS[type]
        

class MaltSocket(bpy.types.NodeSocket):
    
    bl_label = "Malt Node Socket"

    def on_type_update(self, context):
        self.node.on_socket_update(self)

    data_type: bpy.props.StringProperty(update=on_type_update,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    array_size: bpy.props.IntProperty(default=0, update=on_type_update,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    default_initialization: bpy.props.StringProperty(default='',
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    def show_in_material_panel_update(self, context=None):
        key = self.node.get_input_parameter_name(self.name)
        show_in_children = self.node.id_data.malt_parameters.show_in_children
        if key in show_in_children.keys():
            show_in_children[key].boolean = self.show_in_material_panel

    show_in_material_panel: bpy.props.BoolProperty(default=True, update=show_in_material_panel_update,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    active: bpy.props.BoolProperty(default=True,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    ui_label: bpy.props.StringProperty()

    def is_instantiable_type(self):
        return self.data_type.startswith('sampler') == False

    def get_source_reference(self, target_type=None):
        assert(self.active)
        if not self.is_instantiable_type() and not self.is_output and self.get_linked() is not None:
            self.get_linked().get_source_reference()
        else:
            reference = self.node.get_source_socket_reference(self)
            if target_type and target_type != self.data_type:
                cast_function = self.node.id_data.cast(self.data_type, target_type)
                return f'{cast_function}({reference})'
            return reference
    
    def get_source_global_reference(self):
        assert(self.active)
        transpiler = self.id_data.get_transpiler()
        result = transpiler.global_reference(self.node.get_source_name(), self.name)
        if len(result) > 63:
            #Blender dictionary keys are limited to 63 characters
            import xxhash
            result = result[:59] + xxhash.xxh32_hexdigest(result)[:4]
        return result
    
    def is_struct_member(self):
        return '.' in self.name
    
    def get_struct_socket(self):
        if self.is_struct_member():
            struct_socket_name = self.name.split('.')[0]
            if self.is_output:
                return self.node.outputs[struct_socket_name]
            else:
                return self.node.inputs[struct_socket_name]
        return None
    
    def get_source_initialization(self):
        assert(self.active)
        if self.get_linked():
            return self.get_linked().get_source_reference(self.data_type)
        elif self.default_initialization != '':
            return self.default_initialization
        elif self.is_struct_member() and (self.get_struct_socket().get_linked() or self.get_struct_socket().default_initialization != ''):
            return None
        else:
            return self.get_source_global_reference()

    def get_linked(self, ignore_muted=True):
        def get_linked_internal(socket):
            if socket.is_linked == False and ignore_muted:
                return None
            else:
                try: link = socket.links[0]
                except: return None #socket.links can be empty even if is_linked is true!?!?!
                if ignore_muted and link.is_muted:
                    return None
                linked = link.to_socket if socket.is_output else link.from_socket
                if isinstance(linked.node, bpy.types.NodeReroute):
                    sockets = linked.node.inputs if linked.is_output else linked.node.outputs
                    if len(sockets) == 0:
                        return None
                    return get_linked_internal(sockets[0])
                else:
                    return linked if linked.active else None
        return get_linked_internal(self)
    
    def get_ui_label(self, print_type=True):
        name = self.ui_label
        if print_type == False:
            return name

        type = self.data_type
        if self.array_size > 0:
            type += f'[{self.array_size}]'
        
        if self.is_output:
            return f'({type}) : {name}'
        else:
            return f'{name} : ({type})'
    
    def draw(self, context, layout, node, text):
        if self.active == False:
            layout.active = False
            layout.label(text=text)
        elif context.region.type != 'UI' or self.get_source_global_reference() == self.get_source_initialization():
            preferences = bpy.context.preferences.addons['BlenderMalt'].preferences
            text = self.get_ui_label(preferences.show_socket_types)
            node.draw_socket(context, layout, self, text)
            if context.region.type == 'UI':
                icon = 'HIDE_OFF' if self.show_in_material_panel else 'HIDE_ON'
                layout.prop(self, 'show_in_material_panel', text='', icon=icon)
    
    def setup_shape(self):
        from Malt.PipelineParameters import Parameter
        base_type = True
        try:
            Parameter.from_glsl_type(self.data_type)
        except:
            base_type = False
        array_type = self.array_size > 0
        if base_type:
            if array_type:
                self.display_shape = 'CIRCLE_DOT'
            else:
                self.display_shape = 'CIRCLE'
        else:
            if array_type:
                self.display_shape = 'SQUARE_DOT'
            else:
                self.display_shape = 'SQUARE'

    def draw_color(self, context, node):
        color = get_type_color(self.data_type)
        if self.active == False:
            color = list(color)
            color[3] = 0.25
        return color


classes = [
    MaltSocket
]

def register():
    for _class in classes: bpy.utils.register_class(_class)

def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)
