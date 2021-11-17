# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy    
from BlenderMalt.MaltNodes.MaltNode import MaltNode


class MaltFunctionNode(bpy.types.Node, MaltNode):
    
    bl_label = "Function Node"
    
    def malt_setup(self):
        function = self.get_function()
        if self.first_setup:
            self.name = function['name']

        inputs = {}
        outputs = {}

        if function['type'] != 'void':
            outputs['result'] = {'type': function['type']} #TODO: Array return type
        for parameter in function['parameters']:
            if parameter['io'] in ['out','inout']:
                outputs[parameter['name']] = parameter
            if parameter['io'] in ['','in','inout']:
                inputs[parameter['name']] = parameter
        
        self.setup_sockets(inputs, outputs)

    function_type : bpy.props.StringProperty(update=MaltNode.setup)

    def get_function(self):
        graph = self.id_data.get_pipeline_graph()
        if self.function_type in graph.functions:
            return graph.functions[self.function_type]
        else:
            return self.id_data.get_library()['functions'][self.function_type]

    def get_source_socket_reference(self, socket):
        transpiler = self.id_data.get_transpiler()
        if transpiler.is_instantiable_type(socket.data_type):
            return transpiler.parameter_reference(self.get_source_name(), socket.name)
        else:
            source = self.get_source_code(transpiler)
            return source.splitlines()[-1].split('=')[-1].split(';')[0]

    def get_source_code(self, transpiler):
        function = self.get_function()
        source_name = self.get_source_name()

        post_parameter_initialization = ''
        for input in self.inputs:
            if input.is_struct_member():
                initialization = input.get_source_initialization()
                if initialization:
                    post_parameter_initialization += transpiler.asignment(input.get_source_reference(), initialization)

        parameters = []
        for parameter in function['parameters']:
            initialization = None
            if parameter['io'] in ['','in','inout']:
                socket = self.inputs[parameter['name']]
                initialization = socket.get_source_initialization()
            parameters.append(initialization)

        return transpiler.call(function, source_name, parameters, post_parameter_initialization)

    
classes = [
    MaltFunctionNode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

