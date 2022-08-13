import bpy
from BlenderMalt.MaltNodes.Nodes.MaltFunctionNode import MaltFunctionNodeBase

class MaltFunctionSubCategoryNode(bpy.types.Node, MaltFunctionNodeBase):

    bl_label = "Function SubCategory Node"

    subcategory : bpy.props.StringProperty(options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def get_function_enums(self, context=None):
        items = []
        for key, function in self.id_data.get_full_library()['functions'].items():
            if function['meta'].get('internal'):
                continue
            subcategory = function['meta'].get('subcategory')
            if subcategory == self.subcategory:
                label = function['meta'].get('label', function['name'].replace('_',' ').title())
                items.append((key, label, label))
        return items
    
    def update_function_enum(self, context=None):
        self.function_type = self.function_enum
        if self.disable_updates == False:
            self.id_data.update()

    function_enum : bpy.props.EnumProperty(name='', items=get_function_enums, update=update_function_enum,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    def malt_setup(self):
        #Keep the correct function when the subcategory list changes
        if self.function_type != '' and self.function_type != self.function_enum:
            try: self.function_enum = self.function_type
            except: pass
        return super().malt_setup()
    
    def should_delete_outdated_links(self):
        return True

    def draw_buttons(self, context, layout):
        r = layout.row(align=True)
        r.context_pointer_set('active_node', self)
        r.prop(self, 'function_enum')
        r.operator('wm.malt_cycle_sub_categories', text='', icon='COLLAPSEMENU')
        return super().draw_buttons(context, layout)
    
    def calc_node_width(self, point_size, dpi) -> float:
        import blf
        blf.size(0, point_size, dpi)
        max_width = super().calc_node_width(point_size, dpi)
        layout_padding = 70 # account for the spaces on both sides of the enum dropdown
        label = next(enum[1] for enum in self.get_function_enums() if enum[0]==self.function_enum)
        return max(max_width, blf.dimensions(0, label)[0] + layout_padding)

    def draw_label(self):
        if self.hide:
            label = self.get_function()['meta'].get('label', None)
            if label:
                return self.name + ' - ' + label
        return self.name


def register():
    bpy.utils.register_class(MaltFunctionSubCategoryNode)

def unregister():
    bpy.utils.unregister_class(MaltFunctionSubCategoryNode)