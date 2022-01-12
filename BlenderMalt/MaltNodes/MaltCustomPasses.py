import bpy

from BlenderMalt import MaltPipeline

class MaltIOParameter(bpy.types.PropertyGroup):

    def get_parameter_enums(self, context=None):
        types = ['None']
        bridge = MaltPipeline.get_bridge()
        if bridge and self.graph_type in bridge.graphs:
            graph = bridge.graphs[self.graph_type]
            if self.io_type in graph.graph_io.keys():
                if self.is_output:
                    types = graph.graph_io[self.io_type].dynamic_output_types
                else:
                    types = graph.graph_io[self.io_type].dynamic_input_types
        return [(type, type, type) for type in types]
    
    def get_parameter(self):
        try:
            return self.get_parameter_enums().index(tuple(self['PARAMETER']))
        except:
            return 0

    def set_parameter(self, value):
        self['PARAMETER'] = self.get_parameter_enums()[value]

    graph_type : bpy.props.StringProperty()
    io_type : bpy.props.StringProperty()
    is_output : bpy.props.BoolProperty()
    parameter : bpy.props.EnumProperty(items=get_parameter_enums, get=get_parameter, set=set_parameter)

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

    io : bpy.props.CollectionProperty(type=MaltCustomIO)

class MaltGraphType(bpy.types.PropertyGroup):

    custom_passes : bpy.props.CollectionProperty(type=MaltCustomPasses)

def setup_default_passes(graphs):
    world = bpy.context.scene.world
    for name, graph in graphs.items():
        if graph.graph_type == graph.SCENE_GRAPH:
            if name not in world.malt_graph_types:
                world.malt_graph_types.add().name = name
            graph_type = world.malt_graph_types[name]
            if 'Default' not in graph_type.custom_passes:
                graph_type.custom_passes.add().name = 'Default'
            for custom_pass in graph_type.custom_passes:
                for name, io in graph.graph_io.items():
                    is_new = False
                    if name not in custom_pass.io:
                        custom_pass.io.add().name = name
                        is_new = True
                    custom_io = custom_pass.io[name]
                    if is_new:
                        def add_io_parameter(name, type, is_output):
                            parameters = custom_io.outputs if is_output else custom_io.inputs
                            if name not in parameters:
                                parameters.add().name = name
                                parameters[name].graph_type = graph_type.name
                                parameters[name].io_type = io.name
                                parameters[name].is_output = is_output
                                parameters[name].parameter = type
                        for key, type in io.default_dynamic_inputs.items():
                            add_io_parameter(key, type, False)
                        for key, type in io.default_dynamic_outputs.items():
                            add_io_parameter(key, type, True)

class OT_MaltAddCustomPass(bpy.types.Operator):
    bl_idname = "wm.malt_add_custom_pass"
    bl_label = "Malt Add Cusstom Pass"
    bl_options = {'INTERNAL'}

    graph_type : bpy.props.StringProperty()
    name : bpy.props.StringProperty(default='Custom Pass')

    def draw(self, context):
        self.layout.prop(self,'name')

    def execute(self, context):
        new_pass = context.scene.world.malt_graph_types[self.graph_type].custom_passes.add()
        new_pass.name = self.name
        for name in MaltPipeline.get_bridge().graphs[self.graph_type].graph_io.keys():
            new_pass.io.add().name = name
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


classes = [
    MaltIOParameter,
    MaltCustomIO,
    MaltCustomPasses,
    MaltGraphType,
    OT_MaltAddCustomPass,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    bpy.types.World.malt_graph_types = bpy.props.CollectionProperty(type=MaltGraphType)
    
def unregister():
    del bpy.types.World.malt_graph_types
    for _class in reversed(classes): bpy.utils.unregister_class(_class)

