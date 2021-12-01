# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

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
        
        self.pass_type = self.get_pass_type()
        
        self.setup_sockets(inputs, outputs)

    function_type : bpy.props.StringProperty(update=MaltNode.setup)
    pass_material: bpy.props.PointerProperty(type=bpy.types.Material, update=MaltNode.setup)
    show_material_parameters: bpy.props.BoolProperty(default=True)
    pass_type: bpy.props.StringProperty()

    def get_function(self):
        graph = self.id_data.get_pipeline_graph()
        function = None
        if self.function_type in graph.functions:
            function = graph.functions[self.function_type]
        else:
            function = self.id_data.get_library()['functions'][self.function_type]
        from copy import deepcopy
        function = deepcopy(function)
        function['parameters'] += self.get_custom_io()
        return function
    
    def get_pass_type(self):
        graph = self.id_data.get_pipeline_graph()
        if graph.language == 'Python':
            pass_type = graph.nodes[self.function_type].get_pass_type()
            if pass_type:
                return pass_type
        return ''
    
    def get_custom_io(self):
        if self.get_pass_type() != '' and self.pass_material:
            tree = self.pass_material.malt.shader_nodes
            if tree:
                return tree.get_custom_io()
        return []

    def get_source_socket_reference(self, socket):
        transpiler = self.id_data.get_transpiler()
        if transpiler.is_instantiable_type(socket.data_type):
            return transpiler.parameter_reference(self.get_source_name(), socket.name, 'out' if socket.is_output else 'in')
        else:
            source = self.get_source_code(transpiler)
            return source.splitlines()[-1].split('=')[-1].split(';')[0]

    def get_source_code(self, transpiler):
        function = self.get_function()
        source_name = self.get_source_name()

        parameters = []
        post_parameter_initialization = ''
        for input in self.inputs:
            if input.is_struct_member():
                initialization = input.get_source_initialization()
                if initialization:
                    post_parameter_initialization += transpiler.asignment(input.get_source_reference(), initialization)

        for parameter in function['parameters']:
            initialization = None
            if parameter['io'] in ['','in','inout']:
                socket = self.inputs[parameter['name']]
                initialization = socket.get_source_initialization()
            parameters.append(initialization)

        return transpiler.call(function, source_name, parameters, post_parameter_initialization)
    
    def draw_buttons(self, context, layout):
        if self.pass_type != '':
            layout = layout.column()
            row = layout.row(align=True)
            if self.pass_material:
                row.prop(self, 'show_material_parameters',
                    icon = 'DISCLOSURE_TRI_DOWN' if self.show_material_parameters else 'DISCLOSURE_TRI_RIGHT',
                    icon_only=True, emboss=False
                )
            row.template_ID(self, "pass_material")
            def add_or_duplicate():
                if self.pass_material:
                    self.pass_material = self.pass_material.copy()
                else:
                    self.pass_material = bpy.data.materials.new('Material')
                self.setup()
                #self.id_data.update_tag()
                #self.pass_material.update_tag()
            text = '' if self.pass_material else 'New'
            icon = 'DUPLICATE' if self.pass_material else 'ADD'
            row.operator('wm.malt_callback', text=text, icon=icon).callback.set(add_or_duplicate)
            if self.pass_material and self.show_material_parameters:
                self.pass_material.malt.draw_ui(layout.box(),
                    self.id_data.get_pipeline_graph(self.pass_type).file_extension, self.pass_material.malt_parameters)

    
classes = [
    MaltFunctionNode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

