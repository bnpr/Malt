import bpy

from BlenderMalt import MaltPipeline

class MaltIOParameter(bpy.types.PropertyGroup):

    def get_owner(self):
        path = self.path_from_id()
        owner_path = path.rsplit('.',1)[0]
        return self.id_data.path_resolve(owner_path)
    
    def get_parameter_enums(self, context):
        types = ['None']
        owner = self.get_owner()
        graph_type = owner.graph_type
        pass_type = owner.pass_type
        bridge = MaltPipeline.get_bridge()
        if bridge and graph_type in bridge.graphs:
            graph = bridge.graphs[graph_type]
            if pass_type in graph.graph_IO:
                types = graph.graph_IO[pass_type].dynamic_output_types
        return [(type, type, type) for type in types]

    parameter : bpy.props.EnumProperty(items=get_parameter_enums)

    def draw(self, context, layout, owner):
        layout.label(text='', icon='DOT')
        layout.prop(self, 'name', text='')
        layout.prop(self, 'parameter', text='')

class MaltIOArchetype(bpy.types.PropertyGroup):

    def get_graph_enums(self, context):
        types = context.world.malt.graph_types.keys()
        return [(type, type, type) for type in types]
    
    def get_pass_enums(self, context):
        types = ['NONE']
        bridge = MaltPipeline.get_bridge()
        if bridge and self.graph_type in bridge.graphs:
            types = bridge.graphs[self.graph_type].graph_IO.keys()
        return [(type, type, type) for type in types]

    graph_type : bpy.props.EnumProperty(items=get_graph_enums)
    pass_type : bpy.props.EnumProperty(items=get_pass_enums)
    parameters : bpy.props.CollectionProperty(type=MaltIOParameter)
    parameters_index : bpy.props.IntProperty()

    def draw(self, context, layout, owner):
        layout = layout.column()
        row = layout.row()
        row.label(text='', icon='DOT')
        row.prop(self, 'name', text='')
        row = layout.row()
        row.label(text='', icon='BLANK1')
        row.prop(self, 'graph_type', text='')
        row = layout.row()
        row.label(text='', icon='BLANK1')
        row.prop(self, 'pass_type', text='')

class COMMON_UL_UI_List(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        item.draw(context, layout, data)

def malt_template_list(layout, owner, list_property, index_property):
    row = layout.row()
    row.template_list('COMMON_UL_UI_List', '', owner, list_property, owner, index_property)
    col = row.column()
    op = col.operator('wm.malt_list_add', text='', icon='ADD')
    op.list_path = to_json_rna_path(getattr(owner, list_property))
    op = col.operator('wm.malt_list_remove', text='', icon='REMOVE')
    op.list_path = to_json_rna_path(getattr(owner, list_property))
    op.index = getattr(owner, index_property)

class Malt_PipelineIOArchetypesPanel(bpy.types.Panel):
    bl_label = 'Malt IO Archetypes'
    bl_idname = 'WORLD_PT_MALT_Pipeline_IO_Archetypes'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'world'

    def draw(self, context):
        layout = self.layout
        world = context.world
        layout.label(text='Custom Passes:')
        malt_template_list(layout, world, 'io_archetypes', 'io_archetypes_index')
        try:
            layout.label(text='Outputs:')
            active_archetype = world.io_archetypes[world.io_archetypes_index]
            malt_template_list(layout, active_archetype, 'parameters', 'parameters_index')
        except:
            pass

from BlenderMalt.MaltProperties import to_json_rna_path, from_json_rna_path

class OT_MaltListAdd(bpy.types.Operator):
    bl_label = 'Malt List Add'
    bl_idname = "wm.malt_list_add"
    
    list_path : bpy.props.StringProperty()
    
    def execute(self, context):
        from_json_rna_path(self.list_path).add()
        return {'FINISHED'}

class OT_MaltListRemove(bpy.types.Operator):
    bl_label = 'Malt List Remove'
    bl_idname = "wm.malt_list_remove"
    
    list_path : bpy.props.StringProperty()
    index : bpy.props.IntProperty()
    
    def execute(self, context):
        from_json_rna_path(self.list_path).remove(self.index)
        return {'FINISHED'}

classes = [
    MaltIOParameter,
    MaltIOArchetype,
    COMMON_UL_UI_List,
    Malt_PipelineIOArchetypesPanel,
    OT_MaltListAdd,
    OT_MaltListRemove,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    bpy.types.World.io_archetypes = bpy.props.CollectionProperty(type=MaltIOArchetype)
    bpy.types.World.io_archetypes_index = bpy.props.IntProperty()
    
def unregister():
    del bpy.types.World.io_archetypes
    del bpy.types.World.io_archetypes_index
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

