# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from Malt.PipelineParameters import Parameter, Type
import bpy    
from BlenderMalt.MaltProperties import MaltPropertyGroup


class MaltNode():

    malt_parameters : bpy.props.PointerProperty(type=MaltPropertyGroup)

    disable_updates : bpy.props.BoolProperty(name="Disable Updates", default=False)
    
    first_setup : bpy.props.BoolProperty(default=True)

    # Blender will trigger update callbacks even before init and update has finished
    # So we use some wrappers to get a more sane behaviour

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
                    #TODO: deactivate linked, don't delete them?
                    remove.append(current[e])
            for e in remove:
                current.remove(e)
            for name, dic in new.items():
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
                try:
                    current[name].default_initialization = dic['meta']['init']
                except:
                    current[name].default_initialization = ''
        setup(self.inputs, inputs)
        setup(self.outputs, outputs)
        parameters = {}
        for name, input in self.inputs.items():
            parameter = None
            if name in inputs.keys() and isinstance(inputs[name]['type'], Parameter):
                parameter = inputs[name]['type']
            elif input.array_size == 0:
                try:
                    parameter = Parameter.from_glsl_type(input.data_type)
                    parameter.default_value = eval(inputs[name]['meta']['value'])
                except:
                    pass
            if parameter:
                parameters[input.name] = parameter
        self.malt_parameters.setup(parameters, skip_private=False)
        self.setup_socket_shapes()
        if self.first_setup:
            self.setup_width()
    
    def setup_width(self):
        max_len = len(self.name)
        for input in self.inputs.values():
            max_len = max(max_len, len(input.get_ui_label()))
        for output in self.outputs.values():
            max_len = max(max_len, len(output.get_ui_label()))
        #TODO: Measure actual string width
        self.width = max(self.width, max_len * 10)

    def get_source_name(self):
        name = self.name.replace('.','_')
        name = '_' + ''.join(char for char in name if char.isalnum() or char == '_')
        return name.replace('__','_')

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
            if socket.data_type != '' and socket.get_linked() is None and socket.is_struct_member() == False:
                code += transpiler.global_declaration(socket.data_type, socket.array_size, socket.get_source_global_reference())
        return code
    
    def get_source_global_parameters(self, transpiler):
        return self.sockets_to_global_parameters(self.inputs, transpiler)
    
    def setup_socket_shapes(self):
        from itertools import chain
        for socket in chain(self.inputs.values(), self.outputs.values()):
            socket.setup_shape()
    
    def draw_socket(self, context, layout, socket, text):
        layout.label(text=text)
        if socket.is_output == False and socket.is_linked == False and socket.default_initialization == '':
            if socket.is_struct_member() and (socket.get_struct_socket().is_linked or socket.get_struct_socket().default_initialization != ''):
                return
            self.malt_parameters.draw_parameter(layout, socket.name, None, is_node_socket=True)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'MaltTree'
    
    def draw_label(self):
        return self.name

    
classes = []

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

