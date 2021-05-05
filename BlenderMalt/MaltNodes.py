# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import os
import bpy

from BlenderMalt.MaltProperties import MaltPropertyGroup
from BlenderMalt import MaltPipeline

__LIBRARIES = {}    
__EMPTY_LIBRARY = {
    'structs':[],
    'functions':[],
    'paths':[],
}
def get_libraries():
    return __LIBRARIES
def get_empty_library():
    return __EMPTY_LIBRARY

import time
__TIMESTAMP = time.time()

def track_library_changes(force_update=False):
    if bpy.context.scene.render.engine != 'MALT' and force_update == False:
        return 1

    global __LIBRARIES
    global __TIMESTAMP
    start_time = time.time()

    #purge unused libraries
    new_dic = {}
    for tree in bpy.data.node_groups:
        if isinstance(tree, MaltTree):
            src_path = tree.get_library_path()
            if src_path:
                if src_path in __LIBRARIES:
                    new_dic[src_path] = __LIBRARIES[src_path]
                else:
                    new_dic[src_path] = None
    __LIBRARIES = new_dic

    needs_update = set()
    for path, library in __LIBRARIES.items():
        if os.path.exists(path):
            if library is None:
                needs_update.add(path)
            else:
                for sub_path in library['paths']:
                    if os.path.exists(sub_path):
                        # Don't track individual files granularly since macros can completely change them
                        if os.stat(path).st_mtime > __TIMESTAMP:
                            needs_update.add(path)
                            break
    
    if len(needs_update) > 0:
        results = MaltPipeline.get_bridge().reflect_glsl_libraries(needs_update)
        for path, reflection in results.items():
            __LIBRARIES[path] = reflection
        
        for tree in bpy.data.node_groups:
            if isinstance(tree, MaltTree):
                src_path = tree.get_library_path()
                if src_path:
                    if src_path in needs_update:
                        tree.update()
    
    __TIMESTAMP = start_time
    return 0.1

class MaltTree(bpy.types.NodeTree):

    bl_label = "Malt Node Tree"
    bl_icon = 'NODETREE'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT'

    graph_type: bpy.props.StringProperty(name='Type')

    library_source : bpy.props.StringProperty(name="Shader Library", subtype='FILE_PATH')

    def get_library_path(self):
        if self.library_source != '':
            src_path = bpy.path.abspath(self.library_source, library=self.library)
            if os.path.exists(src_path):
                return src_path
        return None
    
    def get_library(self):
        library_path = self.get_library_path()
        if library_path:
            return get_libraries()[library_path]
        else:
            return get_empty_library()

    def get_pipeline_graph(self):
        graphs = MaltPipeline.get_bridge().graphs
        if self.graph_type in graphs:
            return graphs[self.graph_type]
        return None
    
    def get_generated_source_dir(self):
        import os, tempfile
        base_path = '//'
        if bpy.context.blend_data.is_saved == False:
            base_path = tempfile.gettempdir()
        return os.path.join(base_path,'malt-shaders')

    def get_generated_source_path(self):
        import os
        file_prefix = 'temp'
        if bpy.context.blend_data.is_saved:  
            file_prefix = bpy.path.basename(bpy.context.blend_data.filepath).split('.')[0]
        pipeline_graph = self.get_pipeline_graph()
        if pipeline_graph:
            return os.path.join(self.get_generated_source_dir(),'{}-{}{}'.format(file_prefix, self.name, pipeline_graph.file_extension))
        return None
    
    def get_generated_source(self):
        output_node = None
        pipeline_graph = self.get_pipeline_graph()
        if pipeline_graph:
            for node in self.nodes:
                if isinstance(node, MaltIONode) and node.is_output:
                    output_node = node
        nodes = []
        def add_node_inputs(node):
            for input in node.inputs:
                if input.is_linked:
                    new_node = input.links[0].from_node
                    if new_node not in nodes:
                        add_node_inputs(new_node)
                        nodes.append(new_node)

        global_scope = ''
        
        library_path = self.get_library_path()
        if library_path:
            global_scope += '#include "{}"\n'.format(library_path)
        
        for node in self.nodes:
            global_scope += node.get_glsl_uniforms()
        
        code = ''
        if output_node:
            add_node_inputs(output_node)
            for node in nodes:
                code += node.get_glsl_code()
            code += output_node.get_glsl_code()
        
        import textwrap
        code = textwrap.indent(code,'\t')

        return pipeline_graph.generate_source({
            'GLOBAL': global_scope,
            'COMMON_PIXEL_SHADER': code,
        })

    def update(self):
        if MaltPipeline.is_initialized() == False:
            #Blender can call this before fully initializing the blend file. <(T_T)>
            return
        if self.get_pipeline_graph() is None:
            return
        '''
        for link in self.links:
            if link.from_socket.data_type != link.to_socket.data_type:
                self.links.remove(link)
        '''
        source = self.get_generated_source()
        source_dir = bpy.path.abspath(self.get_generated_source_dir())
        source_path = bpy.path.abspath(self.get_generated_source_path())
        import pathlib
        pathlib.Path(source_dir).mkdir(parents=True, exist_ok=True)
        with open(source_path,'w') as f:
            f.write(source)
        from BlenderMalt import MaltMaterial
        MaltMaterial.track_shader_changes()


class NODE_PT_MaltNodeTree(bpy.types.Panel):

    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Malt Nodes"
    bl_label = "Malt Node Tree UI"

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'MaltTree'
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.space_data.node_tree, 'generated_source')

__TYPE_COLORS = {}
def get_type_color(type):
    if type not in __TYPE_COLORS:
        import random, hashlib
        seed = hashlib.sha1(type.encode('ascii')).digest()
        rand = random.Random(seed)
        __TYPE_COLORS[type] = (rand.random(),rand.random(),rand.random(),1.0)
    return __TYPE_COLORS[type]


class MaltSocket(bpy.types.NodeSocket):
    
    bl_label = "Malt Node Socket"

    data_type: bpy.props.StringProperty()
    #TODO: Array

    def get_glsl_reference(self):
        return self.node.get_glsl_socket_reference(self)
    
    def get_glsl_uniform(self):
        return 'U_0{}_0_{}'.format(self.node.get_glsl_name(), self.name)
    
    def get_glsl_uniform_declaration(self):
        return 'uniform {} {};\n'.format(self.data_type, self.get_glsl_uniform())
    
    def get_linked(self):
        if len(self.links) == 0:
            return None
        else:
            link = self.links[0]
            return link.to_socket if self.is_output else link.from_socket
    
    def draw(self, context, layout, node, text):
        text + ' : ' + self.data_type
        node.draw_socket(context, layout, self, text)
    
    def draw_color(self, context, node):
        return get_type_color(self.data_type)
    

class MaltNode():

    def get_glsl_name(self):
        name = self.name.replace('.','_')
        name = '_' + ''.join(char for char in name if char.isalnum() or char == '_')
        return name.replace('__','_')

    def get_glsl_code(self):
        return '/*{} not implemented*/'.format(self)

    def get_glsl_socket_reference(self, socket):
        return '{} /*not implemented*/'.format(socket.name)
    
    def sockets_to_uniforms(self, sockets):
        code = ''
        for socket in sockets:
            if socket.data_type != '' and socket.get_linked() is None:
                code += socket.get_glsl_uniform_declaration()
        return code
    
    def get_glsl_uniforms(self):
        return ''
    
    def draw_socket(self, context, layout, socket, text):
        material = context.active_object.active_material
        tree = self.id_data
        if material and material.malt.shader_nodes is tree:
            uniform = socket.get_glsl_uniform()
            rna = material.malt.parameters.get_rna()
            if uniform in rna.keys() and rna[uniform]['active']:
                material.malt.parameters.draw_ui(layout, mask=[uniform], is_node_socket=True)
                return

        layout.label(text=text)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'MaltTree'
    
    def draw_label(self):
        return self.name


class MaltStructNode(bpy.types.Node, MaltNode):
    
    bl_label = "Struct Node"

    properties: bpy.props.PointerProperty(type=MaltPropertyGroup)

    def setup(self, context):
        malt_parameters = {}

        struct = self.get_struct()
        self.name = self.struct_type
        max_len = len(self.name)
        
        self.inputs.new('MaltSocket', self.struct_type).data_type = self.struct_type
        self.outputs.new('MaltSocket', self.struct_type).data_type = self.struct_type
        for member in struct['members']:
            max_len = max(max_len, len(member['name']) * 2)
            self.inputs.new('MaltSocket', member['name']).data_type = member['type']
            self.outputs.new('MaltSocket', member['name']).data_type = member['type']
        
        self.properties.setup(malt_parameters)
        #TODO: Measure actual string width
        self.width = max_len * 10

    struct_type : bpy.props.StringProperty(update=setup)

    def get_struct(self):
        graph = self.id_data.get_pipeline_graph()
        if self.struct_type in graph.structs:
            return graph.structs[self.struct_type]
        else:
            return self.id_data.get_library()['structs'][self.struct_type]

    def get_glsl_socket_reference(self, socket):
        if socket.name == self.struct_type:
            return self.get_glsl_name()
        else:
            return '{}.{}'.format(self.get_glsl_name(), socket.name)
    
    def struct_input_is_linked(self):
        return self.inputs[self.struct_type].get_linked() is not None

    def get_glsl_code(self):
        code = ''
        node_name = self.get_glsl_name()
        struct_linked = self.struct_input_is_linked()
        
        if struct_linked:
            linked = self.inputs[self.struct_type].get_linked()
            initialization = linked.get_glsl_reference()
            code += '{} {} = {};\n'.format(self.struct_type, node_name, initialization)
        else:
            code += '{} {};\n'.format(self.struct_type, node_name)
        
        for input in self.inputs:
            if input.data_type != self.struct_type:
                if input.get_linked():
                    linked = input.get_linked()
                    code += '{}.{} = {};\n'.format(node_name, input.name, linked.get_glsl_reference())
                elif struct_linked == False:
                    code += '{}.{} = {};\n'.format(node_name, input.name, input.get_glsl_uniform())
        
        return code + '\n'
    
    def get_glsl_uniforms(self):
        code = ''
        struct_linked = self.struct_input_is_linked()
        if struct_linked == False:
            for socket in self.inputs:
                if socket.data_type != self.struct_type and socket.get_linked() is None:
                    code += socket.get_glsl_uniform_declaration()
        return code
    
    def draw_socket(self, context, layout, socket, text):
        if socket.is_output:
            layout.label(text=text)
        else:
            #super() does not work
            MaltNode.draw_socket(self, context, layout, socket, text)
        

class MaltFunctionNode(bpy.types.Node, MaltNode):
    
    bl_label = "Function Node"
    
    def setup(self, context):
        self.inputs.clear()
        self.outputs.clear()
        malt_parameters = {}
        function = self.get_function()
        self.name = self.function_type
        max_len = len(self.name)
        if function['type'] != 'void':
            self.outputs.new('MaltSocket', 'result').data_type = function['type']
        for parameter in function['parameters']:
            max_len = max(max_len, len(parameter['name']) * 2)
            if parameter['io'] in ['out','inout']:
                self.outputs.new('MaltSocket', parameter['name']).data_type = parameter['type']
            if parameter['io'] in ['','in','inout']:
                self.inputs.new('MaltSocket', parameter['name']).data_type = parameter['type']
                #malt_parameters[parameter['name']] = Parameter.from_glsl_type(parameter['type'])
        
        self.properties.setup(malt_parameters)
        #TODO: Measure actual string width
        self.width = max_len * 10

    function_type : bpy.props.StringProperty(update=setup)

    def get_function(self):
        graph = self.id_data.get_pipeline_graph()
        if self.function_type in graph.functions:
            return graph.functions[self.function_type]
        else:
            return self.id_data.get_library()['functions'][self.function_type]

    def get_glsl_socket_reference(self, socket):
        return '{}_0_{}'.format(self.get_glsl_name(), socket.name)

    def get_glsl_code(self):
        code = ''
        function = self.get_function()
        parameters = []
        for parameter in function['parameters']:
            if parameter['io'] in ['out','inout']:
                socket = self.outputs[parameter['name']]
                copy_from = '{}()'.format(socket.data_type)
                linked = socket.get_linked()
                if linked:
                    copy_from = linked.get_glsl_renference()
                code += '{} {} = {};\n'.format(parameter['type'], socket.get_glsl_reference(), copy_from)
                parameters.append(socket.get_glsl_reference())
            if parameter['io'] in ['','in']:
                socket = self.inputs[parameter['name']]
                linked = socket.get_linked()
                if linked:
                    parameters.append(linked.get_glsl_reference())
                else:
                    parameters.append(socket.get_glsl_uniform())
        if function['type'] != 'void':
            code += '{} {} = '.format(function['type'], self.outputs['result'].get_glsl_reference())
        
        code += self.function_type+'('
        for i, parameter in enumerate(parameters):
            code += parameter
            if i < len(parameters) - 1:
                code += ', '
        code += ');\n\n'

        return code
    
    def get_glsl_uniforms(self):
        return self.sockets_to_uniforms(self.inputs)


class MaltIONode(bpy.types.Node, MaltNode):
    
    bl_label = "IO Node"

    properties: bpy.props.PointerProperty(type=MaltPropertyGroup)
    is_output: bpy.props.BoolProperty()

    def setup(self, context):
        malt_parameters = {}
        function = self.get_function()
        self.name = self.io_type + (' Output' if self.is_output else ' Input')
        max_len = len(self.name)
        if function['type'] != 'void':
            self.inputs.new('MaltSocket', 'result').data_type = function['type']
        for parameter in function['parameters']:
            max_len = max(max_len, len(parameter['name']) * 2)
            if parameter['io'] in ['out','inout'] and self.is_output == True:
                self.inputs.new('MaltSocket', parameter['name']).data_type = parameter['type']
                #malt_parameters[parameter['name']] = Parameter.from_glsl_type(parameter['type'])
            if parameter['io'] in ['','in','inout'] and self.is_output == False:
                self.outputs.new('MaltSocket', parameter['name']).data_type = parameter['type']
        
        self.properties.setup(malt_parameters)
        #TODO: Measure actual string width
        self.width = max_len * 10

    io_type : bpy.props.StringProperty(update=setup)

    def get_function(self):
        graph = self.id_data.get_pipeline_graph()
        return graph.graph_IO[self.io_type]

    def get_glsl_socket_reference(self, socket):
        return socket.name
    
    def get_glsl_code(self):
        code = ''
        if self.is_output:
            function = self.get_function()
            for socket in self.inputs:
                if socket.name == 'result':
                    continue
                if socket.get_linked():
                    code += '{} = {};\n'.format(socket.name, socket.get_linked().get_glsl_reference())

            if function['type'] != 'void':
                result = '{}()'.format(function['type'])
                linked = self.inputs['result'].get_linked()
                if linked:
                    result = linked.get_glsl_reference()
                code += 'return {};\n'.format(result)

        return code


class MaltUniformsNode(bpy.types.Node, MaltNode):
    
    bl_label = "Uniforms Node"

    def init(self, context):
        self.name = 'Uniforms'
        self.outputs.new('MaltSocket', 'parameter')
    
    def update(self):
        remove = []
        for i, output in enumerate(self.outputs):
            if output.get_linked() is None:
                remove.append(output)
        for socket in remove:
            self.outputs.remove(socket)
        
        self.outputs.new('MaltSocket', 'parameter')

        for output in self.outputs:
            if output.get_linked():
                linked = output.get_linked()
                output.data_type = linked.data_type
                if output.name.startswith(linked.name) == False:
                    name = linked.name
                    #make sure name is unique
                    while name in self.outputs:
                        if name[-2:].isdigit():
                            number = int(name[-2:]) + 1
                            name = name[:-2] + (str(0) + str(number))[-2:]
                        else:
                            name = name + '_01'
                    output.name = name

    def get_glsl_socket_reference(self, socket):
        return socket.get_glsl_uniform()
    
    def get_glsl_code(self):
        return ''
    
    def get_glsl_uniforms(self):
        code = ''
        for socket in self.outputs:
            if socket.data_type != '':
                code += socket.get_glsl_uniform_declaration()
        return code


class MaltInlineNode(bpy.types.Node, MaltNode):
    
    bl_label = "Inline Code Node"

    def code_update(self, context):
        #update the node tree
        self.id_data.update()

    code : bpy.props.StringProperty(update=code_update)

    def init(self, context):
        self.name = 'Inline Code'
        for input in 'abcdefgh':
            self.inputs.new('MaltSocket', input)
        self.outputs.new('MaltSocket', 'result')
    
    def update(self):
        max = 0
        for i, input in enumerate(self.inputs):
            if input.data_type != '':
                max = i
        for i, input in enumerate(self.inputs):
            input.hide = i > max + 1
        
        from itertools import chain
        for socket in chain(self.inputs, self.outputs):
            linked = socket.get_linked()
            if linked and linked.data_type != '':
                socket.data_type = socket.get_linked().data_type

    def draw_buttons(self, context, layout):
        layout.prop(self, 'code', text='')
    
    def draw_socket(self, context, layout, socket, text):
        layout = layout.row()
        layout.label(text=socket.name)
        if socket.is_output == False:
            layout.prop(socket, 'data_type', text='')

    def get_glsl_socket_reference(self, socket):
        return '{}_0_{}'.format(self.get_glsl_name(), socket.name)
    
    def get_glsl_code(self):
        code = '{} {};\n'.format(self.outputs['result'].data_type, self.outputs['result'].get_glsl_reference())
        code += '{\n'

        for input in self.inputs:
            if input.get_linked():
                code += '   {} {} = {};\n'.format(input.data_type, input.name, input.get_linked().get_glsl_reference())
        if self.code != '':
            code += '   {} = {};\n'.format(self.outputs['result'].get_glsl_reference(), self.code)

        code += '}\n\n'

        return code


def get_pipeline_graph(context):
    if context is None or context.space_data is None or context.space_data.edit_tree is None:
        return None
    return context.space_data.edit_tree.get_pipeline_graph()

def insert_node(layout, type, label, settings = {}):
    operator = layout.operator("node.add_node", text=label)
    operator.type = type
    operator.use_transform = True
    for name, value in settings.items():
        item = operator.settings.add()
        item.name = name
        item.value = value
    return operator

from itertools import chain

class MALT_MT_NodeFunctions(bpy.types.Menu):
    
    bl_label = "Malt Node Functions Menu"

    def draw(self, context):
        layout = self.layout
        graph = get_pipeline_graph(context)
        if graph:
            library_functions = context.space_data.node_tree.get_library()['functions']
            for name in sorted(chain(graph.functions, library_functions)):
                insert_node(self.layout, "MaltFunctionNode", name, settings={
                    'function_type' : repr(name)
                })

class MALT_MT_NodeStructs(bpy.types.Menu):
    
    bl_label = "Malt Node Structs Menu"

    def draw(self, context):
        layout = self.layout
        graph = get_pipeline_graph(context)
        if graph:
            library_structs = context.space_data.node_tree.get_library()['structs']
            for name in sorted(chain(graph.structs,library_structs)):
                insert_node(self.layout, "MaltStructNode", name, settings={
                    'struct_type' : repr(name)
                })

class MALT_MT_NodeInputs(bpy.types.Menu):
    
    bl_label = "Malt Node Inputs Menu"

    def draw(self, context):
        layout = self.layout
        graph = get_pipeline_graph(context)
        if graph:
            for name in sorted(graph.graph_IO):
                insert_node(self.layout, "MaltIONode", name + ' Input', settings={
                    'is_output' : repr(False),
                    'io_type' : repr(name),
            })

class MALT_MT_NodeOutputs(bpy.types.Menu):
    
    bl_label = "Malt Node Outputs Menu"

    def draw(self, context):
        layout = self.layout
        graph = get_pipeline_graph(context)
        if graph:
            for name in sorted(graph.graph_IO):
                insert_node(self.layout, "MaltIONode", name + ' Ouput', settings={
                    'is_output' : repr(True),
                    'io_type' : repr(name),
            })

class MALT_MT_NodeOther(bpy.types.Menu):
    
    bl_label = "Malt Node Other Menu"

    def draw(self, context):
        layout = self.layout
        graph = get_pipeline_graph(context)
        if graph:
            insert_node(self.layout, "MaltUniformsNode", 'Uniforms')
            insert_node(self.layout, "MaltInlineNode", 'Inline Code')

def setup_node_trees():
    for tree in bpy.data.node_groups:
        if tree.bl_idname == 'MaltTree':
            tree.update()

def add_node_ui(self, context):
    if context.space_data.tree_type != 'MaltTree':
        return
    graph = get_pipeline_graph(context)
    if graph:
        self.layout.menu("MALT_MT_NodeFunctions", text='Functions')
        self.layout.menu("MALT_MT_NodeStructs", text='Structs')
        self.layout.menu("MALT_MT_NodeInputs", text='Inputs')
        self.layout.menu("MALT_MT_NodeOutputs", text='Outputs')
        self.layout.menu("MALT_MT_NodeOther", text='Other')

def node_header_ui(self, context):
    if context.space_data.tree_type != 'MaltTree':
        return
    self.layout.prop(context.space_data.node_tree, 'library_source')
    self.layout.prop_search(context.space_data.node_tree, 'graph_type', context.scene.world.malt, 'graph_types',text='')

    
classes = (
    MaltTree,
    NODE_PT_MaltNodeTree,
    MaltSocket,
    #MaltNode,
    MaltStructNode,
    MaltFunctionNode,
    MaltIONode,
    MaltUniformsNode,
    MaltInlineNode,
    MALT_MT_NodeFunctions,
    MALT_MT_NodeStructs,
    MALT_MT_NodeInputs,
    MALT_MT_NodeOutputs,
    MALT_MT_NodeOther,
)

def register():
    for _class in classes: bpy.utils.register_class(_class)

    bpy.types.NODE_MT_add.append(add_node_ui)
    bpy.types.NODE_HT_header.append(node_header_ui)

    bpy.app.timers.register(track_library_changes, persistent=True)
    

def unregister():
    bpy.types.NODE_MT_add.remove(add_node_ui)
    bpy.types.NODE_HT_header.remove(node_header_ui)

    for _class in reversed(classes): bpy.utils.unregister_class(_class)

    bpy.app.timers.unregister(track_library_changes)

