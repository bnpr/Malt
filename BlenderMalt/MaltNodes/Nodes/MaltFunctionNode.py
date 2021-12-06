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
        
        self.setup_sockets(inputs, outputs)
        
        self.pass_type = self.get_pass_type()
        if self.pass_type != '':
            from Malt.PipelineParameters import MaterialParameter
            extension = self.id_data.get_pipeline_graph(self.pass_type).file_extension
            self.malt_parameters.setup(
                {'PASS_MATERIAL': MaterialParameter('', extension)},
                replace_parameters=False,
                skip_private=False
            )

    function_type : bpy.props.StringProperty(update=MaltNode.setup)
    pass_type: bpy.props.StringProperty()

    def get_parameters(self, overrides, resources):
        parameters = MaltNode.get_parameters(self, overrides, resources)
        if self.get_pass_material():
            parameters['CUSTOM_IO'] = self.get_custom_io()
        return parameters

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
    
    def get_pass_material(self):
        if self.get_pass_type() != '' and 'PASS_MATERIAL' in self.malt_parameters.materials.keys():
            return self.malt_parameters.materials['PASS_MATERIAL'].material
    
    def get_custom_io(self):
        material = self.get_pass_material()
        if material:
            tree = material.malt.shader_nodes
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
        
        if self.pass_type != '':
            def add_implicit_parameter(name):
                parameter = transpiler.parameter_reference(self.get_source_name(), name, None)
                initialization = transpiler.global_reference(self.get_source_name(), name)
                nonlocal post_parameter_initialization
                post_parameter_initialization += transpiler.asignment(parameter, initialization)
            add_implicit_parameter('PASS_MATERIAL')
            add_implicit_parameter('CUSTOM_IO')

        return transpiler.call(function, source_name, parameters, post_parameter_initialization)
    
    def draw_buttons(self, context, layout):
        if self.pass_type != '':
            self.malt_parameters.draw_parameter(layout, 'PASS_MATERIAL', None, is_node_socket=True)
    
classes = [
    MaltFunctionNode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

