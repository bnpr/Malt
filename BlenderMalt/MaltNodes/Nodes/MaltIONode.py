# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

import bpy    
from BlenderMalt.MaltNodes.MaltNode import MaltNode
from BlenderMalt.MaltProperties import MaltPropertyGroup

from BlenderMalt.MaltNodes.MaltIOArchetype import *

class MaltIONode(bpy.types.Node, MaltNode):
    
    bl_label = "IO Node"

    properties: bpy.props.PointerProperty(type=MaltPropertyGroup)
    is_output: bpy.props.BoolProperty()

    custom_pass: bpy.props.StringProperty()
    allow_custom_pass : bpy.props.BoolProperty(default=False)

    def malt_setup(self):
        function = self.get_function()
        if self.first_setup:
            self.name = self.io_type + (' Output' if self.is_output else ' Input')
        
        self.graph_type = self.id_data.graph_type
        self.pass_type = self.io_type
        
        if len(self.get_dynamic_parameter_types()) > 0:
            self.allow_custom_pass = True
        else:
            self.allow_custom_pass = False
            self.custom_pass = ''

        inputs = {}
        outputs = {}
        
        if function['type'] != 'void' and self.is_output:
            inputs['result'] = {'type': function['type']}
        for parameter in function['parameters']:
            if parameter['io'] in ['out','inout'] and self.is_output:
                if parameter['io'] == 'inout':
                    if 'meta' not in parameter: parameter['meta'] = {}
                    parameter['meta']['init'] = parameter['name']
                inputs[parameter['name']] = parameter
            if parameter['io'] in ['','in','inout'] and self.is_output == False:
                outputs[parameter['name']] = parameter
        
        for parameter in self.custom_parameters:
            list = inputs if self.is_output else outputs
            if parameter.name not in list.keys(): #Don't override properties
                list[parameter.name] = {
                    'type': parameter.parameter
                }
        
        self.setup_sockets(inputs, outputs)

    io_type : bpy.props.StringProperty(update=MaltNode.setup)

    custom_parameters : bpy.props.CollectionProperty(type=MaltIOParameter)
    custom_parameters_index : bpy.props.IntProperty()

    def get_function(self):
        graph = self.id_data.get_pipeline_graph()
        try:
            return graph.graph_IO[self.io_type].function
        except:
            return graph.graph_IO[self.io_type]
    
    def get_dynamic_parameter_types(self):
        try:
            graph = self.id_data.get_pipeline_graph()
            if self.is_output:
                return graph.graph_IO[self.io_type].dynamic_output_types
            else: 
                return graph.graph_IO[self.io_type].dynamic_input_types
        except:
            return []
    
    def is_custom_socket(self, socket):
        parameters = [parameter['name'] for parameter in self.get_function()['parameters']]
        if (socket.name == 'result' and self.is_output) or socket.name in parameters:
            return False
        elif socket.name in self.custom_parameters.keys():
            return True
        else:
            return False

    def get_source_socket_reference(self, socket):
        io = 'out' if self.is_output else 'in'
        transpiler = self.id_data.get_transpiler()
        if self.is_custom_socket(socket):
            return socket.get_source_global_reference()
        else:
            return transpiler.io_parameter_reference(socket.name, io)
    
    def get_source_code(self, transpiler):
        code = ''
        if self.is_output:
            function = self.get_function()
            for socket in self.inputs:
                if self.is_custom_socket(socket):
                    code += transpiler.asignment(
                        transpiler.global_output_reference(socket.get_source_global_reference()),
                        socket.get_source_initialization())
                else:
                    if socket.name == 'result':
                        code += transpiler.declaration(socket.data_type, socket.array_size, None)
                    initialization = socket.get_source_initialization()
                    if initialization:
                        code += transpiler.asignment(socket.get_source_reference(), initialization)

            if function['type'] != 'void':
                code += transpiler.result(self.inputs['result'].get_source_reference())

        return code
    
    def get_source_global_parameters(self, transpiler):
        src = MaltNode.get_source_global_parameters(self, transpiler)
        if self.is_output:
            graph_io = self.id_data.get_pipeline_graph().graph_IO[self.io_type]
            try:
                shader_type = graph_io.shader_type
                index = graph_io.custom_output_start_index
            except:
                shader_type = None
                index = None
            for socket in self.inputs:
                if self.is_custom_socket(socket):
                    src += transpiler.global_output_declaration(socket.data_type, socket.get_source_global_reference(), index, shader_type)
                    index += 1
        else:
            for socket in self.outputs:
                if self.is_custom_socket(socket):
                    src += transpiler.global_declaration(socket.data_type, socket.array_size, socket.get_source_global_reference())
        return src
    
    def draw_buttons(self, context, layout):
        graph = self.id_data.get_pipeline_graph()
        if graph.pass_type == graph.SCENE_PASS:
            layout.prop(self, 'custom_pass', text='Custom Pass')
    
    def draw_buttons_ext(self, context, layout):
        if self.allow_custom_pass:
            layout.operator("wm.malt_callback", text='Reload', icon='FILE_REFRESH').callback.set(self.setup)
            row = layout.row()
            row.template_list('COMMON_UL_UI_List', '', self, 'custom_parameters', self, 'custom_parameters_index')
            col = row.column()
            def add_custom_socket():
                new_param = self.custom_parameters.add()
                new_param.graph_type = self.id_data.graph_type
                new_param.pass_type = self.io_type
                new_param.is_output = self.is_output
                name = f"Custom {'Output' if new_param.is_output else 'Input'}"
                index = 1
                #TODO: Check against default parameters
                while f'{name} {index}' in self.custom_parameters.keys():
                    index += 1
                new_param.name = f'{name} {index}'
            col.operator("wm.malt_callback", text='', icon='ADD').callback.set(add_custom_socket)
            def remove_custom_socket():
                self.custom_parameters.remove(self.custom_parameters_index)
            col.operator("wm.malt_callback", text='', icon='REMOVE').callback.set(remove_custom_socket)
    
    def draw_label(self):
        return self.name if self.custom_pass == '' else f'{self.name} : {self.custom_pass}'
    
classes = [
    MaltIONode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

