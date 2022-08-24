from Malt.PipelineParameters import Type, Parameter, MaterialParameter, GraphParameter
import bpy    
from BlenderMalt.MaltNodes.MaltNode import MaltNode


class MaltFunctionNodeBase(MaltNode):
        
    def malt_setup(self):
        pass_type = self.get_pass_type()
        if pass_type != '':
            self.pass_graph_type, self.pass_graph_io_type = pass_type.split('.')

        function = self.get_function(skip_overrides=False, find_replacement=True)

        inputs = {}
        outputs = {}

        if function['type'] != 'void':
            outputs['result'] = {'type': function['type']} #TODO: Array return type
        for parameter in function['parameters']:
            if parameter['io'] in ['out','inout']:
                outputs[parameter['name']] = parameter
            if parameter['io'] in ['','in','inout']:
                inputs[parameter['name']] = parameter
        
        show_in_material_panel = function['meta'].get('category', '') == 'Parameters'
        
        self.setup_sockets(inputs, outputs, show_in_material_panel=show_in_material_panel)
        
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
                        {'PASS_MATERIAL': MaterialParameter(None, graph.file_extension, self.pass_graph_type)},
                        replace_parameters=False,
                        skip_private=False
                    )

    function_type : bpy.props.StringProperty(update=MaltNode.setup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    pass_graph_type: bpy.props.StringProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    pass_graph_io_type: bpy.props.StringProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def get_parameters(self, overrides, resources):
        parameters = super().get_parameters(overrides, resources)
        parameters['CUSTOM_IO'] = self.get_custom_io()
        if 'PASS_GRAPH' in self.malt_parameters.graphs.keys():
            try: parameters['PASS_GRAPH'] = self.malt_parameters.get_parameter('PASS_GRAPH', overrides, resources)
            except: pass
        if 'PASS_MATERIAL' in self.malt_parameters.materials.keys():
            try: parameters['PASS_MATERIAL'] = self.malt_parameters.get_parameter('PASS_MATERIAL', overrides, resources)
            except: pass
        return parameters
    
    def find_replacement_function(self):
        library = self.id_data.get_full_library()['functions']
        for key, function in library.items():
            try:
                for replace in eval(function['meta']['replace']).split(','):
                    if replace in self.function_type:
                        self.function_type = key
                        return function
            except:
                pass
        parameters = set()
        from itertools import chain
        for socket in chain(self.inputs.keys(), self.outputs.keys()):
            parameters.add(socket)
        key, function = None, None
        matching_parameters = 0
        total_parameters = 0
        for _key, _function in library.items():
            if _function['name'] in self.function_type:
                matching_count = 0
                for parameter in _function['parameters']:
                    if parameter['name'] in parameters:
                        matching_count += 1
                if (key is None or matching_count > matching_parameters or 
                (matching_count == matching_parameters and len(_function['parameters']) < total_parameters)):
                    total_parameters = len(_function['parameters'])
                    key = _key
                    function = _function
        if _key:
            self.function_type = key
            return function

    def get_function(self, skip_overrides=True, find_replacement=False):
        graph = self.id_data.get_pipeline_graph()
        function = None
        if self.function_type in graph.functions:
            function = graph.functions[self.function_type]
        elif self.function_type in self.id_data.get_library()['functions']:
            function = self.id_data.get_library()['functions'][self.function_type]
        elif find_replacement:
            function = self.find_replacement_function()
        if function:
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
    
    def get_pass_node_tree(self):
        if self.pass_graph_type != '':
            graph = self.id_data.get_pipeline_graph(self.pass_graph_type)
            if graph.graph_type == graph.GLOBAL_GRAPH:
                if graph.language == 'Python':
                    return self.malt_parameters.graphs['PASS_GRAPH'].graph
                else:
                    material = self.malt_parameters.materials['PASS_MATERIAL'].material
                    if material:
                        return material.malt.shader_nodes
    
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
            if input.active and input.is_struct_member():
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
            layout.operator('wm.malt_callback', text='Reload Sockets', icon='FILE_REFRESH').callback.set(self.setup, 'Reload Sockets')
            graph = self.id_data.get_pipeline_graph(self.pass_graph_type)
            if graph.graph_type == graph.GLOBAL_GRAPH:
                if graph.language == 'Python':
                    self.malt_parameters.draw_parameter(layout, 'PASS_GRAPH', None, is_node_socket=True)
                else:
                    self.malt_parameters.draw_parameter(layout, 'PASS_MATERIAL', None, is_node_socket=True)


class MaltFunctionNode(bpy.types.Node, MaltFunctionNodeBase):
    bl_label = "Function Node"

classes = [
    MaltFunctionNode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

