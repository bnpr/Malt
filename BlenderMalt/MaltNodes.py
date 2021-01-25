# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import bpy
from bpy.types import NodeTree, Node, NodeSocket
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

import json

from Malt.GL.Shader import GLSL_Reflection
from Malt.Parameter import Parameter
from BlenderMalt.MaltProperties import MaltPropertyGroup

class MaltTree(NodeTree):
    
    bl_label = "Malt Node Tree"
    bl_icon = 'NODETREE'

    def update_source(self, context):
        source = open(self.source_path, 'r').read()
        functions = GLSL_Reflection.reflect_functions(source)
        self.functions_json = json.dumps(functions)

    source_path: bpy.props.StringProperty(update=update_source, subtype='FILE_PATH')
    functions_json: bpy.props.StringProperty()


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
        layout.prop(context.space_data.node_tree, 'source_path')


class MaltNodeCategory(NodeCategory):
    
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'MaltTree'


def node_items(context):
    if context is None or context.space_data is None or context.space_data.edit_tree is None:
        return
    
    node_tree = context.space_data.edit_tree
    for function in json.loads(node_tree.functions_json):
        print('store :', repr(json.dumps(function)))
        yield NodeItem("MaltNode", label=function['name'], settings={
            'function_json' : repr(json.dumps(function))
        })


class MaltSocket(NodeSocket):
    
    bl_label = "Malt Node Socket"

    data_type: bpy.props.StringProperty()
    
    def draw(self, context, layout, node, text):
        label = text + ': ' + self.data_type

        if self.is_output or self.is_linked:
            layout.label(text=label)
        else:
            node.properties.draw_ui(layout, [self.name])
    
    def draw_color(self, context, node):
        return (0.5,1.0,0.5,1.0)
    

class MaltTreeNode:
    
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'MaltTree'


class MaltNode(Node, MaltTreeNode):
    
    bl_label = "Custom Node"

    properties: bpy.props.PointerProperty(type=MaltPropertyGroup)

    def setup(self, context):
        malt_parameters = {}

        function = json.loads(self.function_json)
        self.name = function['name']
        if function['type'] != 'void':
            self.outputs.new('MaltSocket', 'return').data_type = function['type']
        for parameter in function['parameters']:
            if parameter['io'] in ['out','inout']:
                self.outputs.new('MaltSocket', parameter['name']).data_type = parameter['type']
            if parameter['io'] in ['','in','inout']:
                self.inputs.new('MaltSocket', parameter['name']).data_type = parameter['type']
                malt_parameters[parameter['name']] = Parameter.from_glsl_type(parameter['type'])
        
        self.properties.setup(malt_parameters)           

    function_json : bpy.props.StringProperty(update=setup)

    def init(self, context):
        return
        
    def update(self):
        return
        print('UPDATE')
        
    def update_sockets(self, context):
        return
        print("update sockets")
        '''
        self.inputs.clear()
        for description in self.input_descriptions:
            socket = self.inputs.new(description.get_type(), description.name)
        self.outputs.clear()
        for description in self.output_descriptions:
            socket = self.outputs.new(description.get_type(), description.name)
        '''

    def copy(self, node):
        return
        print("Copying from node ", node)

    def free(self):
        return
        print("Removing node ", self, ", Goodbye!")

    def draw_buttons(self, context, layout):
        pass

    def draw_label(self):
        return self.name


classes = (
    MaltTree,
    NODE_PT_MaltNodeTree,
    MaltSocket,
    MaltNode,
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
