# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

from copy import copy, deepcopy
import bpy
from bpy.types import NodeTree, Node, NodeSocket
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

import json

from Malt.GL.Shader import GLSL_Reflection
from Malt.Parameter import Parameter
from BlenderMalt.MaltProperties import MaltPropertyGroup
from BlenderMalt import MaltPipeline

class MaltTree(NodeTree):
    
    bl_label = "Malt Node Tree"
    bl_icon = 'NODETREE'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT'

    def update_source(self, context):
        source = open(self.source_path, 'r').read()
        functions = GLSL_Reflection.reflect_functions(source)
        print(functions)
        self.functions_json = json.dumps(functions)

    generated_source: bpy.props.StringProperty()
    source_path: bpy.props.StringProperty(update=update_source, subtype='FILE_PATH')
    functions_json: bpy.props.StringProperty()

    def update(self):
        print('UPDATE NODE TREE')
        output_node = None
        pipeline_nodes = MaltPipeline.get_bridge().nodes
        if pipeline_nodes:
            for node in self.nodes:
                if isinstance(node, MaltIONode) and node.is_output:
                    print('has output')
                    output_node = node
        nodes = []
        def add_node_inputs(node):
            for input in node.inputs:
                if input.is_linked:
                    new_node = input.links[0].from_node
                    if new_node not in nodes:
                        add_node_inputs(new_node)
                        nodes.append(new_node)

        def to_glsl_name(node, variable_name):
            return '_' + node.name.replace('.','_').replace(' ','_') + '__' + variable_name

        code = ''
        if output_node:
            add_node_inputs(output_node)
            for node in nodes:
                '''
                if isintance(node, MaltIONode):
                    for output in node.ouputs:
                        type = output.data_type
                        variable = name + '__' + output.name
                        line = '{} {} = {}.{}'
                '''
                if isinstance(node, MaltFunctionNode):
                    function = json.loads(node.function_json)
                    variables = []
                    parameters = []
                    for parameter in function['parameters']:
                        #if parameter['io'] == 'out':
                        #    code += '{} {};\n'.format(parameter['type'], to_glsl_name(node.name, parameter['name']))
                        if parameter['io'] in ['','in','inout']:
                            socket = node.inputs[parameter['name']]
                            if socket.is_linked:
                                link = socket.links[0]
                                parameters.append(to_glsl_name(link.from_node, link.from_socket.name))
                            else:
                                parameters.append(parameter['type'] + '()')
                    if function['type'] != 'void':
                        code += '{} {} = '.format(function['type'], to_glsl_name(node, 'result'))
                    
                    code += function['name']+'('
                    for i, parameter in enumerate(parameters):
                        code += parameter
                        if i < len(parameters) - 1:
                            code += ', '
                    code += ');\n\n'
        
        print('-'*10)
        print(code)
        print('-'*10)
        self.generated_source = code


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


class MaltNodeCategory(NodeCategory):
    
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'MaltTree'


def node_items(context):
    if context is None or context.space_data is None or context.space_data.edit_tree is None:
        return
    
    nodes = MaltPipeline.get_bridge().nodes
    if nodes:
        for name, function in nodes['functions'].items():
            yield NodeItem("MaltFunctionNode", label=name, settings={
                'function_json' : repr(json.dumps(function))
            })
        for function in nodes['graph functions']:
            yield NodeItem("MaltIONode", label=function['name'] + ' Input', settings={
                'is_output' : repr(False), 
                'function_json' : repr(json.dumps(function))
            })
            yield NodeItem("MaltIONode", label=function['name'] + ' Output', settings={
                'is_output' : repr(True),
                'function_json' : repr(json.dumps(function))
            })
        for name, struct in nodes['structs'].items():
            yield NodeItem("MaltStructNode", label=name, settings={
                'struct_json' : repr(json.dumps(struct))
            })

__TYPE_COLORS = {}
def get_type_color(type):
    if type not in __TYPE_COLORS:
        import random, hashlib
        seed = hashlib.sha1(type.encode('ascii')).digest()
        rand = random.Random(seed)
        __TYPE_COLORS[type] = (rand.random(),rand.random(),rand.random(),1.0)
        print(type, seed, __TYPE_COLORS[type])
    return __TYPE_COLORS[type]

class MaltSocket(NodeSocket):
    
    bl_label = "Malt Node Socket"

    data_type: bpy.props.StringProperty()
    #TODO: Array
    
    def draw(self, context, layout, node, text):
        label = text + ' ' + self.data_type

        layout.label(text=label)
        return
        
        if self.is_output or self.is_linked:
            layout.label(text=label)
        else:
            node.properties.draw_ui(layout, mask=[self.name], is_node_socket=True)
    
    def draw_color(self, context, node):
        return get_type_color(self.data_type)# (0.5,1.0,0.5,1.0)
    

class MaltTreeNode:
    
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'MaltTree'
    
    def draw_label(self):
        return self.name


class MaltStructNode(Node, MaltTreeNode):
    
    bl_label = "Custom Node"

    properties: bpy.props.PointerProperty(type=MaltPropertyGroup)

    def setup(self, context):
        malt_parameters = {}

        struct = json.loads(self.struct_json)
        self.name = struct['name']
        max_len = len(self.name)
        
        self.inputs.new('MaltSocket', struct['name']).data_type = struct['name']
        self.outputs.new('MaltSocket', struct['name']).data_type = struct['name']
        for member in struct['members']:
            max_len = max(max_len, len(member['name']) * 2)
            self.inputs.new('MaltSocket', member['name']).data_type = member['type']
            self.outputs.new('MaltSocket', member['name']).data_type = member['type']
                #malt_parameters[parameter['name']] = Parameter.from_glsl_type(parameter['type'])
        
        self.properties.setup(malt_parameters)
        #TODO: Measure actual string width
        self.width = max_len * 10

    struct_json : bpy.props.StringProperty(update=setup)


class MaltFunctionNode(Node, MaltTreeNode):
    
    bl_label = "Custom Node"

    properties: bpy.props.PointerProperty(type=MaltPropertyGroup)

    def setup(self, context):
        malt_parameters = {}

        function = json.loads(self.function_json)
        self.name = function['name']
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

    function_json : bpy.props.StringProperty(update=setup)

class MaltIONode(Node, MaltTreeNode):
    
    bl_label = "Custom Node"

    properties: bpy.props.PointerProperty(type=MaltPropertyGroup)
    is_output: bpy.props.BoolProperty()

    def setup(self, context):
        try:
            malt_parameters = {}

            function = json.loads(self.function_json)
            self.name = function['name'] + ' Output' if self.is_output else ' Input'
            max_len = len(self.name)
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
        except:
            import traceback
            traceback.print_exc()

    function_json : bpy.props.StringProperty(update=setup)


classes = (
    MaltTree,
    NODE_PT_MaltNodeTree,
    MaltSocket,
    MaltStructNode,
    MaltFunctionNode,
    MaltIONode,
)


def register():
    for _class in classes: bpy.utils.register_class(_class)

    nodeitems_utils.register_node_categories(
        'MALT_NODES',
        [ MaltNodeCategory('MALTNODES', "Malt Nodes", items=node_items) ]
    )
    

def unregister():
    nodeitems_utils.unregister_node_categories('MALT_NODES')

    for _class in classes: bpy.utils.unregister_class(_class)


if __name__ == "__main__":
    register()
