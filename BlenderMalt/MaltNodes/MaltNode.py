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
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    # Blender will trigger update callbacks even before init and update has finished
    # So we use some wrappers to get a more sane behaviour

    def get_parameters(self, overrides, resources):
        return self.malt_parameters.get_parameters(overrides, resources)

    def _disable_updates_wrapper(self, function):
        tree = self.id_data
        tree.disable_updates = True
        self.disable_updates = True
        try:
            function()
        except:
            import traceback
            traceback.print_exc()
        tree.disable_updates = False
        self.disable_updates = False

    def init(self, context):
        self._disable_updates_wrapper(self.malt_init)
        
    def setup(self, context=None):
        self._disable_updates_wrapper(self.malt_setup)
        self.first_setup = False
        if self.subscribed == False:
            tree = self.id_data
            bpy.msgbus.subscribe_rna(key=self.path_resolve('name', False),
                owner=self, args=(None,), notify=lambda _ : tree.update())
            self.subscribed = True

    def update(self):
        if self.disable_updates:
            return
        self._disable_updates_wrapper(self.malt_update)
        
    def malt_init(self):
        pass

    def malt_setup(self):
        pass
    
    def malt_update(self):
        pass

    def on_socket_update(self, socket):
        pass

    def setup_sockets(self, inputs, outputs, expand_structs=True):
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
                if len(e.links) == 0 or self.should_delete_outdated_links():
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
                node_label = self.name.replace('.', ' ')
                parameter.label = f'{node_label}.{label}'
                parameters[name] = parameter
        self.malt_parameters.setup(parameters, skip_private=False)
        self.setup_socket_shapes()
        if self.first_setup:
            self.setup_width()
    
    def should_delete_outdated_links(self):
        return False
    
    def setup_width(self):
        size = bpy.context.preferences.ui_styles[0].widget_label.points
        dpi = 72 #dont use bpy.context.preferences.system.dpi because that is influenced by the UI scale but the node widths are not
        import blf
        blf.size(0, size, dpi)
        header_padding = 36 # account for a little space for the arrow icon + extra padding on the side of a label
        socket_padding = 31 # account for little offset of the text from the node border

        def adjust_width(width, text, scale=1, padding=0):
            new_width = blf.dimensions(0, text)[0] * scale + padding
            print(text, 'has', new_width, 'width')
            result = max(width, new_width)
            return result

        print('-'*20)
        # max_width = blf.dimensions(0, self.draw_label())[0] + header_padding
        max_width = adjust_width(0, self.draw_label(), padding=header_padding)
        for input in self.inputs.values():
            scale = 2 
            if input.default_initialization or '.' in input.name:
                scale = 1
            # max_width = max(max_width, blf.dimensions(0, input.get_ui_label())[0] * scale + socket_padding)
            max_width = adjust_width(max_width, input.get_ui_label(), scale=scale, padding=socket_padding*scale)
        for output in self.outputs.values():
            # max_width = max(max_width, blf.dimensions(0, output.get_ui_label())[0] + socket_padding)
            max_width = adjust_width(max_width, output.get_ui_label(), padding=socket_padding)
        # self.width = max(max_width, 140)
        self.width = max_width
        print('Final Width:', self.width)
        return self.width

    def get_source_name(self):
        return self.id_data.get_transpiler().get_source_name(self.name)

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
            self.malt_parameters.draw_parameter(get_layout(), socket.name, text, is_node_socket=True)
            for key in self.malt_parameters.get_rna().keys():
                if key.startswith(socket.name + ' @ '):
                    self.malt_parameters.draw_parameter(get_layout(), key, None, is_node_socket=True)
        else:
            layout.label(text=text)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'MaltTree'
    
    def draw_label(self):
        return self.name.replace('_', ' ')

    
classes = []

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

