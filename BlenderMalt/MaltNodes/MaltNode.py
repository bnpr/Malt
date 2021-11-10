# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy    

class MaltNode():

    malt_parameters : bpy.props.PointerProperty(type=MaltPropertyGroup)

    disable_updates : bpy.props.BoolProperty(name="Disable Updates", default=False)
    
    first_setup : bpy.props.BoolProperty(default=True)

    # Blender will trigger update callbacks even before init and update has finished
    # So we use some wrappers to get a more sane behaviour

    def _disable_updates_wrapper(self, function):
        tree = self.id_data
        tree.disable_updates = True
        self.disable_updates = True
        try:
            function()
        except:
            import traceback
            traceback.print_exc()
        tree.disable_updates = False
        self.disable_updates = False

    def init(self, context):
        self._disable_updates_wrapper(self.malt_init)
        
    def setup(self, context=None):
        self._disable_updates_wrapper(self.malt_setup)
        self.first_setup = False

    def update(self):
        if self.disable_updates:
            return
        self._disable_updates_wrapper(self.malt_update)
        
    def malt_init(self):
        pass

    def malt_setup(self):
        pass
    
    def malt_update(self):
        pass

    def on_socket_update(self, socket):
        pass

    def setup_sockets(self, inputs, outputs, expand_structs=True):
        from Malt.Parameter import Parameter, Type
        def _expand_structs(sockets):
            result = {}
            for name, dic in sockets.items():
                result[name] = dic
                struct_type = self.id_data.get_struct_type(dic['type'])
                if struct_type:
                    for member in struct_type['members']:
                        result[f"{name}.{member['name']}"] = member
            return result
        if expand_structs:
            inputs = _expand_structs(inputs)
            outputs = _expand_structs(outputs)
        def setup(current, new):
            remove = []
            for e in current.keys():
                if e not in new:
                    #TODO: deactivate linked, don't delete them?
                    remove.append(current[e])
            for e in remove:
                current.remove(e)
            for name, dic in new.items():
                type = dic['type']
                size = dic['size'] if 'size' in dic else 0
                if name not in current:
                    current.new('MaltSocket', name)
                if isinstance(type, Parameter):
                    current[name].data_type = type.type_string()
                    current[name].array_size = 0 #TODO
                else:
                    current[name].data_type = type
                    current[name].array_size = size
                try:
                    current[name].default_initialization = dic['meta']['init']
                except:
                    current[name].default_initialization = ''
        setup(self.inputs, inputs)
        setup(self.outputs, outputs)
        parameters = {}
        for name, input in self.inputs.items():
            parameter = None
            if name in inputs.keys() and isinstance(inputs[name]['type'], Parameter):
                parameter = inputs[name]['type']
            elif input.array_size == 0:
                try:
                    parameter = Parameter.from_glsl_type(input.data_type)
                    parameter.default_value = eval(inputs[name]['meta']['value'])
                except:
                    pass
            if parameter:
                parameters[input.name] = parameter
        self.malt_parameters.setup(parameters, skip_private=False)
        self.setup_socket_shapes()
        if self.first_setup:
            self.setup_width()
    
    def setup_width(self):
        max_len = len(self.name)
        for input in self.inputs.values():
            max_len = max(max_len, len(input.get_ui_label()))
        for output in self.outputs.values():
            max_len = max(max_len, len(output.get_ui_label()))
        #TODO: Measure actual string width
        self.width = max(self.width, max_len * 10)

    def get_source_name(self):
        name = self.name.replace('.','_')
        name = '_' + ''.join(char for char in name if char.isalnum() or char == '_')
        return name.replace('__','_')

    def get_source_code(self, transpiler):
        if self.id_data.get_source_language() == 'GLSL':
            return '/*{} not implemented*/'.format(self)
        elif self.id_data.get_source_language() == 'Python':
            return '# {} not implemented'.format(self)

    def get_source_socket_reference(self, socket):
        if self.id_data.get_source_language() == 'GLSL':
            return '/*{} not implemented*/'.format(socket.name)
        elif self.id_data.get_source_language() == 'Python':
            return '# {} not implemented'.format(socket.name)
    
    def sockets_to_global_parameters(self, sockets, transpiler):
        code = ''
        for socket in sockets:
            if socket.data_type != '' and socket.get_linked() is None and socket.is_struct_member() == False:
                code += transpiler.global_declaration(socket.data_type, socket.array_size, socket.get_source_global_reference())
        return code
    
    def get_source_global_parameters(self, transpiler):
        return self.sockets_to_global_parameters(self.inputs, transpiler)
    
    def setup_socket_shapes(self):
        from itertools import chain
        for socket in chain(self.inputs.values(), self.outputs.values()):
            socket.setup_shape()
    
    def draw_socket(self, context, layout, socket, text):
        layout.label(text=text)
        if socket.is_output == False and socket.is_linked == False and socket.default_initialization == '':
            if socket.is_struct_member() and (socket.get_struct_socket().is_linked or socket.get_struct_socket().default_initialization != ''):
                return
            self.malt_parameters.draw_parameter(layout, socket.name, None, is_node_socket=True)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'MaltTree'
    
    def draw_label(self):
        return self.name


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


class MaltIONode(bpy.types.Node, MaltNode):
    
    bl_label = "IO Node"

    properties: bpy.props.PointerProperty(type=MaltPropertyGroup)
    is_output: bpy.props.BoolProperty()

    def malt_setup(self):
        function = self.get_function()
        if self.first_setup:
            self.name = self.io_type + (' Output' if self.is_output else ' Input')

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
        return graph.graph_IO[self.io_type]

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


class MaltArrayIndexNode(bpy.types.Node, MaltNode):
    
    bl_label = "Array Index Node"

    def malt_init(self):
        self.setup()
        
    def malt_setup(self):
        if self.first_setup:
            self.name = 'Array Index'
        self.setup_sockets({ 'array' : {'type': '', 'size': 1}, 'index' : {'type': Parameter(0, Type.INT) }},
            {'element' : {'type': ''} })
        
    def malt_update(self):
        inputs = { 
            'array' : {'type': '', 'size': 1},
            'index' : {'type': Parameter(0, Type.INT) }
        }
        outputs = { 'element' : {'type': ''} }
        
        linked = self.inputs['array'].get_linked()
        if linked and linked.array_size > 0:
            inputs['array']['type'] = linked.data_type
            inputs['array']['size'] = linked.array_size
            outputs['element']['type'] = linked.data_type

        self.setup_sockets(inputs, outputs)

    def get_source_socket_reference(self, socket):
        return '{}_0_{}'.format(self.get_source_name(), socket.name)
    
    def get_source_code(self, transpiler):
        array = self.inputs['array']
        index = self.inputs['index']
        element = self.outputs['element']
        element_reference = index.get_source_global_reference()
        if index.get_linked():
            element_reference = index.get_linked().get_source_reference()
        initialization = '{}[{}]'.format(array.get_linked().get_source_reference(), element_reference)
        return transpiler.declaration(element.data_type, element.array_size, element.get_source_reference(), initialization)

    
classes = (
    MaltTree,
    NODE_PT_MaltNodeTree,
    MaltSocket,
    #MaltNode,
    MaltStructNode,
    MaltFunctionNode,
    MaltIONode,
    MaltInlineNode,
    MaltArrayIndexNode,
    MALT_MT_NodeFunctions,
    MALT_MT_NodeStructs,
    MALT_MT_NodeInputs,
    MALT_MT_NodeOutputs,
    MALT_MT_NodeOther,
)

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

