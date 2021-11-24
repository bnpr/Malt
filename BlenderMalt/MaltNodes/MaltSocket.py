# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

import bpy

__TYPE_COLORS = {}
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

    data_type: bpy.props.StringProperty(update=on_type_update)

    array_size: bpy.props.IntProperty(default=0, update=on_type_update)
    
    default_initialization: bpy.props.StringProperty(default='')
    
    show_in_material_panel: bpy.props.BoolProperty(default=True)

    def is_instantiable_type(self):
        return self.data_type.startswith('sampler') == False
    
    def get_source_name(self):
        return self.id_data.get_transpiler().get_source_name(self.name)

    def get_source_reference(self, target_type=None):
        if not self.is_instantiable_type() and not self.is_output and self.get_linked() is not None:
            self.get_linked().get_source_reference()
        else:
            reference = self.node.get_source_socket_reference(self)
            if target_type and target_type != self.data_type:
                cast_function = self.node.id_data.cast(self.data_type, target_type)
                return f'{cast_function}({reference})'
            return reference
    
    def get_source_global_reference(self):
        return self.id_data.get_transpiler().global_reference(self.node.get_source_name(), self.name)
    
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
        if self.is_linked:
            return self.get_linked().get_source_reference(self.data_type)
        elif self.default_initialization != '':
            return self.default_initialization
        elif self.is_struct_member() and (self.get_struct_socket().is_linked or self.get_struct_socket().default_initialization != ''):
            return None
        else:
            return self.get_source_global_reference()

    def get_linked(self):
        def get_linked_internal(socket):
            if len(socket.links) == 0:
                return None
            else:
                link = socket.links[0]
                linked = link.to_socket if socket.is_output else link.from_socket
                if isinstance(linked.node, bpy.types.NodeReroute):
                    sockets = linked.node.inputs if linked.is_output else linked.node.outputs
                    if len(sockets) == 0:
                        return None
                    return get_linked_internal(sockets[0])
                else:
                    return linked
        return get_linked_internal(self)
    
    def get_ui_label(self):
        type = self.data_type
        if self.array_size > 0:
            type += f'[{self.array_size}]'
        if self.is_output:
            return f'({type}) : {self.name}'
        else:
            return f'{self.name} : ({type})'
    
    def draw(self, context, layout, node, text):
        if context.region.type != 'UI' or self.get_source_global_reference() == self.get_source_initialization():
            text = self.get_ui_label()
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
        return get_type_color(self.data_type)


classes = [
    MaltSocket
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

