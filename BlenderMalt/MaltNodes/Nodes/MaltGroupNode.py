from Malt.PipelineParameters import Parameter, Type
import bpy    
from BlenderMalt.MaltNodes.Nodes.MaltFunctionNode import MaltFunctionNodeBase
from BlenderMalt.MaltNodes.MaltNodeTree import MaltTree


class MaltGroupNode(bpy.types.Node, MaltFunctionNodeBase):

    bl_idname = 'MaltGroupNode'
    bl_label = "Group Node"

    def poll_group(self, tree: MaltTree):
        group_type = self.get_graph_type_from_parent(self.id_data)

        def is_target_nested_in_source(target: MaltTree, source: MaltTree):
            if source is None:
                return False
            for node in (n for n in source.nodes.values() if isinstance(n, MaltGroupNode)):
                if node.group is target or is_target_nested_in_source(node.group, target):
                    return True
            return False

        return (
            tree.bl_idname == 'MaltTree' 
            and tree.graph_type == group_type
            and not tree == self.id_data
            and not is_target_nested_in_source(self.id_data, tree)
        )
    
    @staticmethod
    def get_graph_type_from_parent(malt_tree: MaltTree) -> str:
        graph_type: str = malt_tree.graph_type
        suffix = ' (Group)'
        if not graph_type.endswith(suffix):
            graph_type += suffix
        return graph_type
    
    def update_group(self, context):
        self.setup(context)
        self.setup_width() #has to be called explicitely because 'setup' will only call 'setup_width' in some cases

    group : bpy.props.PointerProperty(type=bpy.types.NodeTree, poll=poll_group, update=update_group)

    def create_new_group(self) -> MaltTree:
        nt = bpy.data.node_groups.new('Malt Node Tree', 'MaltTree')
        nt.graph_type = self.get_graph_type_from_parent(self.id_data)
        self.group = nt
        return nt

    def get_linked_node_tree(self):
        return self.group

    def get_function(self, skip_overrides=True, find_replacement=False):
        return self.group.get_group_function()
    
    def get_source_global_parameters(self, transpiler):
        src = f'#include "{self.group.get_generated_source_path()}"\n\n'
        return src + super().get_source_global_parameters(transpiler)

    def draw_buttons(self, context, layout):
        from BlenderMalt.MaltNodes.MaltNodeTree import set_node_tree
        from BlenderMalt.MaltNodes.MaltNodeUITools import OT_MaltAddNodeGroup
        row = layout.row(align=True)
        row.template_ID(self, 'group', new=OT_MaltAddNodeGroup.bl_idname)
        if self.group is not None:
            row.operator('wm.malt_callback', text = '', icon = 'GREASEPENCIL').callback.set(
                lambda: set_node_tree(context, self.group, self)
            )
    
    def calc_node_width(self, point_size, dpi) -> float:
        import blf
        blf.size(0, point_size, dpi)

        button_padding = 150 #Magic number to account for the other buttons on the node UI
        if getattr(self.group, 'users', 0) > 1:
            button_padding += 30

        width = super().calc_node_width(point_size, dpi)
        width = max(width, blf.dimensions(0, getattr(self.group, 'name', ''))[0] + button_padding)
        return width

classes = [
    MaltGroupNode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

