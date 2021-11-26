import bpy

from BlenderMalt import MaltPipeline

class MaltIOParameter(bpy.types.PropertyGroup):

    def get_parameter_enums(self, context):
        types = ['None']
        bridge = MaltPipeline.get_bridge()
        if bridge and self.graph_type in bridge.graphs:
            graph = bridge.graphs[self.graph_type]
            if self.pass_type in graph.graph_IO:
                if self.is_output:
                    types = graph.graph_IO[self.pass_type].dynamic_output_types
                else:
                    types = graph.graph_IO[self.pass_type].dynamic_input_types
        return [(type, type, type) for type in types]

    graph_type : bpy.props.StringProperty()
    pass_type : bpy.props.StringProperty()
    is_output : bpy.props.BoolProperty()
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

class Malt_PipelineIOArchetypesPanel(bpy.types.Panel):
    bl_label = 'Malt IO Archetypes'
    bl_idname = 'WORLD_PT_MALT_Pipeline_IO_Archetypes'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'world'

    def draw(self, context):
        from BlenderMalt.MaltUtils import malt_template_list
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

classes = [
    MaltIOParameter,
    MaltIOArchetype,
    Malt_PipelineIOArchetypesPanel,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    bpy.types.World.io_archetypes = bpy.props.CollectionProperty(type=MaltIOArchetype)
    bpy.types.World.io_archetypes_index = bpy.props.IntProperty()
    
def unregister():
    del bpy.types.World.io_archetypes
    del bpy.types.World.io_archetypes_index
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

