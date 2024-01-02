import bpy    
from BlenderMalt.MaltNodes.MaltNode import MaltNode
from BlenderMalt.MaltProperties import MaltPropertyGroup
from BlenderMalt.MaltNodes.MaltCustomPasses import *


class MaltIONode(bpy.types.Node, MaltNode):
    
    bl_label = "IO Node"

    properties: bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    is_output: bpy.props.BoolProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def get_custom_pass_enums(self, context):
        custom_passes = ['Default']
        if self.allow_custom_pass:
            custom_passes = context.scene.world.malt_graph_types[self.id_data.graph_type].custom_passes.keys()
        return [(p,p,p) for p in custom_passes]
        
    custom_pass: bpy.props.EnumProperty(items=get_custom_pass_enums,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    allow_custom_pass : bpy.props.BoolProperty(default=False,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    allow_custom_parameters : bpy.props.BoolProperty(default=False,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def malt_setup(self, copy=None):
        function = self.get_function()
        
        self.graph_type = self.id_data.graph_type
        self.pass_type = self.io_type
        
        graph = self.id_data.get_pipeline_graph()
        self.allow_custom_pass = graph.graph_type == graph.SCENE_GRAPH
        self.allow_custom_parameters = len(self.get_dynamic_parameter_types()) > 0

        inputs = {}
        outputs = {}
        
        if function['type'] != 'void' and self.is_output:
            inputs['result'] = {'type': function['type']}
        for parameter in function['parameters']:
            if parameter['io'] in ['out','inout'] and self.is_output:
                if parameter['io'] == 'inout':
                    if 'meta' not in parameter: parameter['meta'] = {}
                    parameter['meta']['default'] = parameter['name']
                inputs[parameter['name']] = parameter
            if parameter['io'] in ['','in','inout'] and self.is_output == False:
                outputs[parameter['name']] = parameter
        
        for parameter in self.get_custom_parameters():
            list = inputs if self.is_output else outputs
            if parameter.name not in list.keys(): #Don't override properties
                list[parameter.name] = {
                    'type': parameter.parameter
                }
        
        self.setup_sockets(inputs, outputs, copy=copy)

    io_type : bpy.props.StringProperty(update=MaltNode.setup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    custom_parameters : bpy.props.CollectionProperty(type=MaltIOParameter,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'})
    custom_parameters_index : bpy.props.IntProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def get_function(self):
        graph = self.id_data.get_pipeline_graph()
        return graph.graph_io[self.io_type].function
    
    def get_custom_pass_io(self):
        if self.allow_custom_pass and self.allow_custom_parameters:
            world = bpy.context.scene.world
            return world.malt_graph_types[self.id_data.graph_type].custom_passes[self.custom_pass].io[self.io_type]
    
    def get_custom_parameters(self):
        if self.allow_custom_parameters:
            if self.allow_custom_pass:
                io = self.get_custom_pass_io()
                return io.outputs if self.is_output else io.inputs
            else:
                return self.custom_parameters
        else:
            return {}
    
    def get_dynamic_parameter_types(self):
        graph = self.id_data.get_pipeline_graph()
        if self.is_output:
            return graph.graph_io[self.io_type].dynamic_output_types
        else: 
            return graph.graph_io[self.io_type].dynamic_input_types
    
    def is_custom_socket(self, socket):
        parameters = [parameter['name'] for parameter in self.get_function()['parameters']]
        if (socket.name == 'result' and self.is_output) or socket.name in parameters:
            return False
        elif socket.name in self.get_custom_parameters().keys():
            return True
        else:
            return False

    def get_source_socket_reference(self, socket):
        transpiler = self.id_data.get_transpiler()
        io = 'out' if self.is_output else 'in'
        if self.is_custom_socket(socket):
            return transpiler.custom_io_reference(io, self.io_type, socket.name)
        else:
            return transpiler.io_parameter_reference(socket.name, io)
    
    def get_source_code(self, transpiler):
        code = ''
        if self.is_output:
            function = self.get_function()
            custom_outputs = ''
            for socket in self.inputs:
                if socket.active == False:
                    continue
                if self.is_custom_socket(socket):
                    custom_outputs += transpiler.asignment(self.get_source_socket_reference(socket), socket.get_source_initialization())
                else:
                    if socket.name == 'result':
                        code += transpiler.declaration(socket.data_type, socket.array_size, socket.name)
                    initialization = socket.get_source_initialization()
                    if initialization:
                        code += transpiler.asignment(socket.get_source_reference(), initialization)
            if custom_outputs != '':
                graph_io = self.id_data.get_pipeline_graph().graph_io[self.io_type]
                try: io_wrap = graph_io.io_wrap
                except: io_wrap = ''
                code += transpiler.preprocessor_wrap(io_wrap, custom_outputs)
            if function['type'] != 'void':
                code += transpiler.result(self.inputs['result'].get_source_reference())

        return code
    
    def get_source_global_parameters(self, transpiler):
        src = MaltNode.get_source_global_parameters(self, transpiler)
        if self.id_data.is_group():
            return src
        custom_outputs = ''
        graph_io = self.id_data.get_pipeline_graph().graph_io[self.io_type]
        index = graph_io.custom_output_start_index
        for key, parameter in self.get_custom_parameters().items():
            if parameter.is_output:
                socket = self.inputs[key]
                custom_outputs += transpiler.custom_output_declaration(socket.data_type, key, index, self.io_type)
                index += 1
            else:
                socket = self.outputs[key]
                src += transpiler.global_declaration(parameter.parameter, 0, self.get_source_socket_reference(socket))
        if custom_outputs != '':
            try: io_wrap = graph_io.io_wrap
            except: io_wrap = ''
            src += transpiler.preprocessor_wrap(io_wrap, custom_outputs)
        return src
    
    def draw_buttons(self, context, layout):
        return #TODO: only 1 custom pass signature for now
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
                self.id_data.reload_nodes()
                for tree in bpy.data.node_groups:
                    if tree.bl_idname == 'MaltTree' and tree is not self.id_data:
                        for node in tree.nodes:
                            if hasattr(node, 'get_linked_node_tree') and node.get_linked_node_tree() is self.id_data:
                                tree.reload_nodes()
                                tree.update_ext(force_update=True, force_track_shader_changes=False)
                                break
                self.id_data.update_ext(force_update=True)
                                
            layout.operator("wm.malt_callback", text='Reload', icon='FILE_REFRESH').callback.set(refresh, 'Reload')
            def draw_parameters_list(owner, parameters_key):
                row = layout.row()
                index_key = f'{parameters_key}_index'
                row.template_list('COMMON_UL_UI_List', '', owner, parameters_key, owner, index_key)
                col = row.column()
                parameters = getattr(owner, parameters_key)
                index = getattr(owner, index_key)
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
                add_row = col.row()
                graph = self.id_data.get_pipeline_graph()
                if (self.is_output and graph.language == 'GLSL' and
                len(parameters) >= (8 - graph.graph_io[self.io_type].custom_output_start_index) and
                self.id_data.graph_type.endswith("(Group)") == False): 
                    add_row.enabled = False
                add_row.operator("wm.malt_callback", text='', icon='ADD').callback.set(add_custom_socket, 'Add')
                def remove_custom_socket():
                    parameters.remove(index)
                col.operator("wm.malt_callback", text='', icon='REMOVE').callback.set(remove_custom_socket, 'Remove')
                def move_up():
                    if index > 0:
                        parameters.move(index, index - 1)
                        setattr(owner, index_key, index - 1)
                col.operator("wm.malt_callback", text='', icon='TRIA_UP').callback.set(move_up, 'Move Up')
                def move_down():
                    if index < len(parameters) - 1:
                        parameters.move(index, index + 1)
                        setattr(owner, index_key, index + 1)
                col.operator("wm.malt_callback", text='', icon='TRIA_DOWN').callback.set(move_down, 'Move Down')

            if self.allow_custom_pass:
                draw_parameters_list(self.get_custom_pass_io(), 'outputs' if self.is_output else 'inputs')
            else:
                draw_parameters_list(self, 'custom_parameters')
    
    
classes = [
    MaltIONode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)
