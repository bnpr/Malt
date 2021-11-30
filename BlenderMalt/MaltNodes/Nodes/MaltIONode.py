# Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license. 

import bpy    
from BlenderMalt.MaltNodes.MaltNode import MaltNode
from BlenderMalt.MaltProperties import MaltPropertyGroup

from BlenderMalt.MaltNodes.MaltCustomPasses import *

class MaltIONode(bpy.types.Node, MaltNode):
    
    bl_label = "IO Node"

    properties: bpy.props.PointerProperty(type=MaltPropertyGroup)
    is_output: bpy.props.BoolProperty()

    def get_custom_pass_enums(self, context):
        custom_passes = ['Default']
        if self.allow_custom_pass:
            custom_passes = context.scene.world.malt_graph_types[self.id_data.graph_type].custom_passes.keys()
        return [(p,p,p) for p in custom_passes]
        
    custom_pass: bpy.props.EnumProperty(items=get_custom_pass_enums)
    allow_custom_pass : bpy.props.BoolProperty(default=False)
    allow_custom_parameters : bpy.props.BoolProperty(default=False)

    def malt_setup(self):
        function = self.get_function()
        if self.first_setup:
            self.name = self.io_type + (' Output' if self.is_output else ' Input')
        
        self.graph_type = self.id_data.graph_type
        self.pass_type = self.io_type
        
        graph = self.id_data.get_pipeline_graph()
        self.allow_custom_pass = graph.pass_type == graph.SCENE_PASS
        self.allow_custom_parameters = len(self.get_dynamic_parameter_types()) > 0

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
        
        for parameter in self.get_custom_parameters():
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
    
    def get_custom_parameters(self):
        if self.allow_custom_parameters:
            if self.allow_custom_pass:
                io = bpy.context.scene.world.malt_graph_types[self.id_data.graph_type].custom_passes[self.custom_pass].io[self.io_type]
                return io.outputs if self.is_output else io.inputs
            else:
                return self.custom_parameters
        else:
            return {}
    
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
        elif socket.name in self.get_custom_parameters().keys():
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
        if self.allow_custom_pass and (self.is_output or self.allow_custom_parameters):
            row = layout.row(align=True)
            row.prop(self, 'custom_pass', text='Custom Pass')
            row.operator('wm.malt_add_custom_pass', text='', icon='ADD').graph_type = self.id_data.graph_type
            if self.custom_pass != 'Default':
                def remove():
                    custom_passes = context.scene.world.malt_graph_types[self.id_data.graph_type].custom_passes
                    custom_passes.remove(custom_passes.find(self.custom_pass))
                    #self.custom_pass = 'Default'
                row.operator('wm.malt_callback', text='', icon='REMOVE').callback.set(remove)

    
    def draw_buttons_ext(self, context, layout):
        if self.allow_custom_parameters:
            def refresh():
                #TODO: Overkill
                for tree in bpy.data.node_groups:
                    if tree.bl_idname == 'MaltTree':
                        tree.reload_nodes()
                        tree.update()
            layout.operator("wm.malt_callback", text='Reload', icon='FILE_REFRESH').callback.set(refresh)
            row = layout.row()
            owner = self
            parameters_key = 'custom_parameters'
            if self.allow_custom_pass:
                owner = context.scene.world.malt_graph_types[self.id_data.graph_type].custom_passes[self.custom_pass].io[self.io_type]
                parameters_key = 'outputs' if self.is_output else 'inputs'
            index_key = f'{parameters_key}_index'
            row.template_list('COMMON_UL_UI_List', '', owner, parameters_key, owner, index_key)
            parameters = getattr(owner, parameters_key)
            index = getattr(owner, index_key)
            col = row.column()
            def add_custom_socket():
                new_param = parameters.add()
                new_param.graph_type = self.id_data.graph_type
                new_param.io_type = self.io_type
                new_param.is_output = self.is_output
                name = f"Custom {'Output' if new_param.is_output else 'Input'}"
                i = 1
                #TODO: Check against default parameters
                while f'{name} {i}' in parameters.keys():
                    i += 1
                new_param.name = f'{name} {i}'
            col.operator("wm.malt_callback", text='', icon='ADD').callback.set(add_custom_socket)
            def remove_custom_socket():
                parameters.remove(index)
            col.operator("wm.malt_callback", text='', icon='REMOVE').callback.set(remove_custom_socket)
    
    
classes = [
    MaltIONode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

