from Malt.PipelineParameters import Parameter, Type
import bpy    
from BlenderMalt.MaltNodes.Nodes.MaltFunctionNode import MaltFunctionNodeBase


class MaltGroupNode(bpy.types.Node, MaltFunctionNodeBase):
    
    bl_label = "Group Node"

    def poll_group(self, tree):
        group_type = self.id_data.graph_type
        if group_type.endswith(' (Group)') == False:
            group_type += ' (Group)'
        return tree.bl_idname == 'MaltTree' and tree.graph_type == group_type
    
    def update_group(self, context):
        self.setup(context)

    group : bpy.props.PointerProperty(type=bpy.types.NodeTree, poll=poll_group, update=update_group)

    def get_linked_node_tree(self):
        return self.group

    def get_function(self, skip_overrides=True, find_replacement=False):
        return self.group.get_group_function()
    
    def get_source_global_parameters(self, transpiler):
        src = f'#include "{self.group.get_generated_source_path()}"\n\n'
        return src + super().get_source_global_parameters(transpiler)

    def draw_buttons(self, context, layout):
        from BlenderMalt.MaltNodes.MaltNodeTree import set_node_tree
        row = layout.row(align=True)
        row.prop(self, 'group', text='')
        row.operator('wm.malt_callback', text = '', icon = 'GREASEPENCIL').callback.set(
            lambda: set_node_tree(context, self.group, self)
        )
    
classes = [
    MaltGroupNode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

