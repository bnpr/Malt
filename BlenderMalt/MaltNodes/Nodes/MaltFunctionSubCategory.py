import bpy
from BlenderMalt.MaltNodes.Nodes.MaltFunctionNode import MaltFunctionNodeBase

class MaltFunctionSubCategoryNode(bpy.types.Node, MaltFunctionNodeBase):

    bl_label = "Function SubCategory Node"

    subcategory : bpy.props.StringProperty(options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def get_function_enums(self, context=None):
        library = self.id_data.get_full_library()
        items = []
        for key in library['subcategories'][self.subcategory]:
            function = library['functions'].get(key)
            if function is None or function['meta'].get('internal'):
                continue
            label = function['meta'].get('label')
            if label is None:
                label = function['name'].replace('_',' ').title()
            items.append((key, label, label))
        return items
    
    def update_function_enum(self, context=None):
        self.function_type = self.function_enum
        if self.disable_updates == False:
            self.id_data.update_ext(force_update=True)

    function_enum : bpy.props.EnumProperty(name='', items=get_function_enums, update=update_function_enum,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    def malt_setup(self, copy=None):
        #Keep the correct function when the subcategory list changes
        if self.function_type != '' and self.function_type != self.function_enum:
            try: self.function_enum = self.function_type
            except:
                try:
                    self.function_type = self.function_enum
                except:
                    self.function_type = self.get_function_enums()[0][0]
        return super().malt_setup(copy=copy)
    
    def should_delete_outdated_links(self):
        return True

    def draw_buttons(self, context, layout):
        r = layout.row(align=True)
        r.context_pointer_set('active_node', self)
        r.prop(self, 'function_enum')
        if context.preferences.addons['BlenderMalt'].preferences.use_subfunction_cycling:
            r.operator('wm.malt_cycle_sub_categories', text='', icon='COLLAPSEMENU')
        return super().draw_buttons(context, layout)
    
    def calc_node_width(self, point_size) -> float:
        import blf
        blf.size(0, point_size)
        max_width = super().calc_node_width(point_size)
        layout_padding = 70 # account for the spaces on both sides of the enum dropdown
        label = next(enum[1] for enum in self.get_function_enums() if enum[0]==self.function_enum)
        return max(max_width, blf.dimensions(0, label)[0] + layout_padding)

    def draw_label(self):
        label = super().draw_label()
        if self.hide:
            label += ' - ' + self.get_function()['meta'].get('label', None)
        return label


def register():
    bpy.utils.register_class(MaltFunctionSubCategoryNode)

def unregister():
    bpy.utils.unregister_class(MaltFunctionSubCategoryNode)
