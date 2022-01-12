# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

from Malt.PipelineParameters import Type, Parameter, MaterialParameter, GraphParameter
import bpy    
from BlenderMalt.MaltNodes.MaltNode import MaltNode

class MaltFunctionNode(bpy.types.Node, MaltNode):
    
    bl_label = "Function Node"
    
    def malt_setup(self):
        pass_type = self.get_pass_type()
        if pass_type != '':
            self.pass_graph_type, self.pass_graph_io_type = pass_type.split('.')

        function = self.get_function(skip_overrides=False)
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
        
        if self.pass_graph_type != '':
            graph = self.id_data.get_pipeline_graph(self.pass_graph_type)
            if graph.graph_type == graph.GLOBAL_GRAPH:
                if graph.language == 'Python':
                    self.malt_parameters.setup(
                        {'PASS_GRAPH': GraphParameter(None, graph.name)},
                        replace_parameters=False,
                        skip_private=False
                    )
                else:
                    self.malt_parameters.setup(
                        {'PASS_MATERIAL': MaterialParameter(None, graph.file_extension)},
                        replace_parameters=False,
                        skip_private=False
                    )

    function_type : bpy.props.StringProperty(update=MaltNode.setup)
    pass_graph_type: bpy.props.StringProperty()
    pass_graph_io_type: bpy.props.StringProperty()

    def get_parameters(self, overrides, resources):
        parameters = MaltNode.get_parameters(self, overrides, resources)
        parameters['CUSTOM_IO'] = self.get_custom_io()
        return parameters

    def get_function(self, skip_overrides=True):
        graph = self.id_data.get_pipeline_graph()
        function = None
        if self.function_type in graph.functions:
            function = graph.functions[self.function_type]
        else:
            function = self.id_data.get_library()['functions'][self.function_type]
        from copy import deepcopy
        function = deepcopy(function)
        function['parameters'] += self.get_custom_io()
        if skip_overrides:
           function['parameters'] = [p for p in function['parameters'] if '@' not in p['name']]
        return function
    
    def get_pass_type(self):
        graph = self.id_data.get_pipeline_graph()
        if graph.language == 'Python':
            pass_type = graph.functions[self.function_type]['pass_type']
            if pass_type:
                return pass_type
        return ''
    
    def get_custom_io(self):
        if self.pass_graph_type != '':
            graph = self.id_data.get_pipeline_graph(self.pass_graph_type)
            if graph.graph_type == graph.GLOBAL_GRAPH:
                tree = None
                if graph.language == 'Python':
                    if 'PASS_GRAPH' in self.malt_parameters.graphs.keys():
                        tree = self.malt_parameters.graphs['PASS_GRAPH'].graph
                else:
                    if 'PASS_MATERIAL' in self.malt_parameters.materials.keys():
                        material = self.malt_parameters.materials['PASS_MATERIAL'].material
                        if material:
                            tree = material.malt.shader_nodes
                if tree:
                    return tree.get_custom_io(self.pass_graph_io_type)
            else:
                world = bpy.context.scene.world
                if world:
                    custom_io = world.malt_graph_types[self.pass_graph_type].custom_passes['Default'].io[self.pass_graph_io_type]
                    result = []
                    for parameter in custom_io.inputs:
                        result.append({
                            'name': parameter.name,
                            'type': 'Texture', #TODO
                            'size': 0,
                            'io': 'in',
                        })
                    for parameter in custom_io.outputs:
                        result.append({
                            'name': parameter.name,
                            'type': 'Texture', #TODO
                            'size': 0,
                            'io': 'out',
                        })
                    return result
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
        
        if self.pass_graph_type != '':
            def add_implicit_parameter(name):
                parameter = transpiler.parameter_reference(self.get_source_name(), name, None)
                initialization = transpiler.global_reference(self.get_source_name(), name)
                nonlocal post_parameter_initialization
                post_parameter_initialization += transpiler.asignment(parameter, initialization)
            graph = self.id_data.get_pipeline_graph(self.pass_graph_type)
            if graph.graph_type == graph.GLOBAL_GRAPH:
                if graph.language == 'Python':
                    add_implicit_parameter('PASS_GRAPH')
                else:
                    add_implicit_parameter('PASS_MATERIAL')
            add_implicit_parameter('CUSTOM_IO')

        return transpiler.call(function, source_name, parameters, post_parameter_initialization)
    
    def draw_buttons(self, context, layout):
        if self.pass_graph_type != '':
            layout.operator('wm.malt_callback', text='Reload Sockets', icon='FILE_REFRESH').callback.set(self.setup)
            graph = self.id_data.get_pipeline_graph(self.pass_graph_type)
            if graph.graph_type == graph.GLOBAL_GRAPH:
                if graph.language == 'Python':
                    self.malt_parameters.draw_parameter(layout, 'PASS_GRAPH', None, is_node_socket=True)
                else:
                    self.malt_parameters.draw_parameter(layout, 'PASS_MATERIAL', None, is_node_socket=True)
    
classes = [
    MaltFunctionNode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

