# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

import bpy    
from BlenderMalt.MaltNodes.MaltNode import MaltNode


class MaltStructNode(bpy.types.Node, MaltNode):
    
    bl_label = "Struct Node"

    def malt_setup(self, context=None):
        if self.first_setup:
            self.name = self.struct_type

        inputs = {}
        inputs[self.struct_type] = {'type' : self.struct_type}
        outputs = {}
        outputs[self.struct_type] = {'type' : self.struct_type}

        self.setup_sockets(inputs, outputs)

    struct_type : bpy.props.StringProperty(update=MaltNode.setup)

    def get_struct(self):
        graph = self.id_data.get_pipeline_graph()
        if self.struct_type in graph.structs:
            return graph.structs[self.struct_type]
        else:
            return self.id_data.get_library()['structs'][self.struct_type]

    def get_source_socket_reference(self, socket):
        if socket.name == self.struct_type:
            return self.get_source_name()
        else:
            return socket.name.replace(self.struct_type, self.get_source_name())
    
    def struct_input_is_linked(self):
        return self.inputs[self.struct_type].get_linked() is not None

    def get_source_code(self, transpiler):
        code = ''
        
        for input in self.inputs:
            initialization = input.get_source_initialization()
            if input.is_struct_member():
                if initialization:
                    code += transpiler.asignment(input.get_source_reference(), initialization)
            else:
                code += transpiler.declaration(input.data_type, 0, self.get_source_name(), initialization)
        
        return code

        
classes = [
    MaltStructNode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

