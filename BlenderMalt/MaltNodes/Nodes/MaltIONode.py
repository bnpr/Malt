# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

import bpy    
from BlenderMalt.MaltNodes.MaltNode import MaltNode
from BlenderMalt.MaltProperties import MaltPropertyGroup


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
        
        self.setup_sockets(inputs, outputs)

    io_type : bpy.props.StringProperty(update=MaltNode.setup)

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
            import traceback
            #traceback.print_exc()
            return []

    def get_source_socket_reference(self, socket):
        io = 'out' if self.is_output else 'in'
        return self.id_data.get_transpiler().io_parameter_reference(socket.name, io)
    
    def get_source_code(self, transpiler):
        code = ''
        if self.is_output:
            function = self.get_function()
            for socket in self.inputs:
                if socket.name == 'result':
                    code += transpiler.declaration(socket.data_type, socket.array_size, None)
                initialization = socket.get_source_initialization()
                if initialization:
                    code += transpiler.asignment(socket.get_source_reference(), initialization)

            if function['type'] != 'void':
                code += transpiler.result(self.inputs['result'].get_source_reference())

        return code
    
    def draw_buttons(self, context, layout):
        graph = self.id_data.get_pipeline_graph()
        if graph.pass_type != graph.GLOBAL_PASS:
            layout.prop(self, 'custom_pass', text='Custom Pass')
    
    def draw_label(self):
        return self.name if self.custom_pass == '' else f'{self.name} : {self.custom_pass}'

    
classes = [
    MaltIONode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

