import bpy
from BlenderMalt.MaltNodes.Nodes.MaltFunctionNode import MaltFunctionNodeBase

class MaltFunctionSubCategoryNode(bpy.types.Node, MaltFunctionNodeBase):

    bl_label = "Function SubCategory Node"

    subcategory : bpy.props.StringProperty(options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def get_function_enums(self, context=None):
        items = []
        for key, function in self.id_data.get_full_library()['functions'].items():
            subcategory = function['meta'].get('subcategory')
            if subcategory == self.subcategory:
                name = function['name'].replace('_',' ')
                items.append((key, name, name))
        return items
    
    def update_function_enum(self, context=None):
        self.function_type = self.function_enum

    function_enum : bpy.props.EnumProperty(name='', items=get_function_enums, update=update_function_enum,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def draw_buttons(self, context, layout):
        layout.prop(self, 'function_enum')
        return super().draw_buttons(context, layout)


def register():
    bpy.utils.register_class(MaltFunctionSubCategoryNode)

def unregister():
    bpy.utils.unregister_class(MaltFunctionSubCategoryNode)