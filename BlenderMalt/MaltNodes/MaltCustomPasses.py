import bpy

from BlenderMalt import MaltPipeline

class MaltIOParameter(bpy.types.PropertyGroup):

    def get_parameter_enums(self, context):
        types = ['None']
        bridge = MaltPipeline.get_bridge()
        if bridge and self.graph_type in bridge.graphs:
            graph = bridge.graphs[self.graph_type]
            if self.io_type in graph.graph_IO:
                if self.is_output:
                    types = graph.graph_IO[self.io_type].dynamic_output_types
                else:
                    types = graph.graph_IO[self.io_type].dynamic_input_types
        return [(type, type, type) for type in types]

    graph_type : bpy.props.StringProperty()
    io_type : bpy.props.StringProperty()
    is_output : bpy.props.BoolProperty()
    parameter : bpy.props.EnumProperty(items=get_parameter_enums)

    def draw(self, context, layout, owner):
        layout.label(text='', icon='DOT')
        layout.prop(self, 'name', text='')
        layout.prop(self, 'parameter', text='')

class MaltCustomIO(bpy.types.PropertyGroup):

    inputs : bpy.props.CollectionProperty(type=MaltIOParameter)
    inputs_index : bpy.props.IntProperty()
    outputs : bpy.props.CollectionProperty(type=MaltIOParameter)
    outputs_index : bpy.props.IntProperty()

class MaltCustomPasses(bpy.types.PropertyGroup):

    def get_graph_enums(self, context):
        types = context.world.malt.graph_types.keys()
        return [(type, type, type) for type in types]
    
    graph_type : bpy.props.EnumProperty(items=get_graph_enums)
    io : bpy.props.CollectionProperty(type=MaltCustomIO)

class MaltGraphType(bpy.types.PropertyGroup):

    custom_passes : bpy.props.CollectionProperty(type=MaltCustomPasses)

def setup_default_passes(graphs):
    world = bpy.context.scene.world
    for name, graph in graphs.items():
        if graph.pass_type == graph.SCENE_PASS:
            if name not in world.malt_graph_types:
                world.malt_graph_types.add().name = name
            graph_type = world.malt_graph_types[name]
            if 'Default' not in graph_type.custom_passes:
                graph_type.custom_passes.add().name = 'Default'
            for custom_pass in graph_type.custom_passes:
                for name, io in graph.graph_IO.items():
                    if name not in custom_pass.io:
                        custom_pass.io.add().name = name

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
    MaltCustomIO,
    MaltCustomPasses,
    MaltGraphType,
    #Malt_PipelineIOArchetypesPanel,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    bpy.types.World.malt_graph_types = bpy.props.CollectionProperty(type=MaltGraphType)
    #bpy.types.World.malt_custom_passes_index = bpy.props.IntProperty()
    
def unregister():
    del bpy.types.World.malt_custom_passes
    #del bpy.types.World.malt_custom_passes_index
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

