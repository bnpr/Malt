# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy    
from BlenderMalt.MaltNodes.MaltNode import MaltNode


class MaltInlineNode(bpy.types.Node, MaltNode):
    
    bl_label = "Inline Code Node"

    def code_update(self, context):
        #update the node tree
        self.id_data.update()

    code : bpy.props.StringProperty(update=code_update)

    def on_socket_update(self, socket):
        self.update()
        self.id_data.update()

    def malt_init(self):
        self.setup()

    def malt_setup(self):
        if self.first_setup:
            self.name = 'Inline Code'
        self.malt_update()
    
    def malt_update(self):
        last = 0
        for i, input in enumerate(self.inputs):
            if input.data_type != '' or input.get_linked():
                last = i + 1
        variables = 'abcdefgh'[:min(last+1,8)]
        
        inputs = {}
        for var in variables:
            inputs[var] = {'type': ''}
            if var in self.inputs:
                input = self.inputs[var]
                linked = self.inputs[var].get_linked()
                if linked and linked.data_type != '':
                    inputs[var] = {'type': linked.data_type, 'size': linked.array_size}
                else:
                    inputs[var] = {'type': input.data_type, 'size': input.array_size}
        
        outputs = { 'result' : {'type': ''} }
        if 'result' in self.outputs:
            out = self.outputs['result'].get_linked()
            if out:
                outputs['result'] = {'type': out.data_type, 'size': out.array_size}
        
        self.setup_sockets(inputs, outputs)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'code', text='')
    
    def draw_socket(self, context, layout, socket, text):
        if socket.is_output == False:
            layout = layout.split(factor=0.66)
            row = layout.row(align=True).split(factor=0.1)
            row.alignment = 'LEFT'
            MaltNode.draw_socket(self, context, row, socket, socket.name)
            layout.prop(socket, 'data_type', text='')
        else:
            MaltNode.draw_socket(self, context, layout, socket, socket.name)

    def get_source_socket_reference(self, socket):
        return '{}_0_{}'.format(self.get_source_name(), socket.name)
    
    def get_source_code(self, transpiler):
        code = ''
        result_socket = self.outputs['result']
        code += transpiler.declaration(result_socket.data_type, result_socket.array_size, result_socket.get_source_reference())

        scoped_code = ''
        for input in self.inputs:
            if input.data_type != '':
                initialization = input.get_source_initialization()
                scoped_code += transpiler.declaration(input.data_type, input.array_size, input.name, initialization)
        if self.code != '':
            scoped_code += transpiler.asignment(self.outputs['result'].get_source_reference(), self.code)

        return code + transpiler.scoped(scoped_code)

    
classes = (
    MaltInlineNode,
)

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

