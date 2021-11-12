# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import os, time
from itertools import chain
from Malt.SourceTranspiler import GLSLTranspiler, PythonTranspiler
import bpy
from BlenderMalt.MaltProperties import MaltPropertyGroup
from BlenderMalt import MaltPipeline

from BlenderMalt.MaltNodes.MaltNode import MaltNode
from BlenderMalt.MaltNodes.Nodes import MaltIONode


def get_pipeline_graph(context):
    if context is None or context.space_data is None or context.space_data.edit_tree is None:
        return None
    return context.space_data.edit_tree.get_pipeline_graph()

class MaltTree(bpy.types.NodeTree):

    bl_label = "Malt Node Tree"
    bl_icon = 'NODETREE'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT'
    
    def poll_material(self, material):
        return material.malt.shader_nodes is self
    
    graph_type: bpy.props.StringProperty(name='Type')

    library_source : bpy.props.StringProperty(name="Shader Library", subtype='FILE_PATH')

    disable_updates : bpy.props.BoolProperty(name="Disable Updates", default=False)

    malt_parameters : bpy.props.PointerProperty(type=MaltPropertyGroup)

    def get_source_language(self):
        return self.get_pipeline_graph().language

    def get_transpiler(self):
        if self.get_source_language() == 'GLSL':
            return GLSLTranspiler
        elif self.get_source_language() == 'Python':
            return PythonTranspiler

    def get_library_path(self):
        if self.library_source != '':
            src_path = bpy.path.abspath(self.library_source, library=self.library)
            if os.path.exists(src_path):
                return src_path
        return None
    
    def get_library(self):
        library_path = self.get_library_path()
        if library_path:
            return get_libraries()[library_path]
        else:
            return get_empty_library()
    
    def get_full_library(self):
        #TODO: Cache
        result = get_empty_library()
        result['functions'].update(self.get_pipeline_graph().functions)
        result['structs'].update(self.get_pipeline_graph().structs)
        result['functions'].update(self.get_library()['functions'])
        result['structs'].update(self.get_library()['structs'])
        return result
    
    def get_pipeline_graph(self):
        bridge = MaltPipeline.get_bridge()
        if bridge and self.graph_type in bridge.graphs:
            return bridge.graphs[self.graph_type]
        return None
    
    def cast(self, from_type, to_type):
        cast_function = f'{to_type}_from_{from_type}'
        lib = self.get_full_library()
        if cast_function in lib['functions']:
            #TODO: If more than 1 parameter, check if they have default values
            if len(lib['functions'][cast_function]['parameters']) == 1:
                return cast_function
        return None
    
    def get_struct_type(self, struct_type):
        lib = self.get_full_library()
        if struct_type in lib['structs']:
            return lib['structs'][struct_type]
        return None
    
    def get_generated_source_dir(self):
        import os, tempfile
        base_path = tempfile.gettempdir()
        if bpy.context.blend_data.is_saved or self.library:
            base_path = bpy.path.abspath('//', library=self.library)
        return os.path.join(base_path,'malt-shaders')

    def get_generated_source_path(self):
        import os
        file_prefix = 'temp'
        if self.library:
            file_prefix = bpy.path.basename(self.library.filepath).split('.')[0]
        elif bpy.context.blend_data.is_saved:  
            file_prefix = bpy.path.basename(bpy.context.blend_data.filepath).split('.')[0]
        pipeline_graph = self.get_pipeline_graph()
        if pipeline_graph:
            return os.path.join(self.get_generated_source_dir(),'{}-{}{}'.format(file_prefix, self.name, pipeline_graph.file_extension))
        return None
    
    def get_generated_source(self):
        output_nodes = []
        linked_nodes = []
        
        pipeline_graph = self.get_pipeline_graph()
        if pipeline_graph:
            for node in self.nodes:
                #TODO: MaltNode.is_result()
                if isinstance(node, MaltIONode) and node.is_output:
                    output_nodes.append(node)
                    linked_nodes.append(node)
        
        def add_node_inputs(node, list):
            for input in node.inputs:
                if input.is_linked:
                    new_node = input.links[0].from_node
                    if new_node not in list:
                        add_node_inputs(new_node, list)
                        list.append(new_node)
                    if new_node not in linked_nodes:
                        linked_nodes.append(new_node)
        
        transpiler = self.get_transpiler()
        def get_source(output):
            nodes = []
            add_node_inputs(output, nodes)
            code = ''
            for node in nodes:
                if isinstance(node, MaltNode):
                    code += node.get_source_code(transpiler) + '\n'
            code += output.get_source_code(transpiler)
            return code

        shader ={}
        for output in output_nodes:
            shader[output.io_type] = get_source(output)
        shader['GLOBAL'] = ''
        library_path = self.get_library_path()
        if library_path:
            shader['GLOBAL'] += '#include "{}"\n'.format(library_path)
        for node in linked_nodes:
            if isinstance(node, MaltNode):
                shader['GLOBAL'] += node.get_source_global_parameters(transpiler)
        return pipeline_graph.generate_source(shader)
    
    def reload_nodes(self):
        self.disable_updates = True
        try:
            for node in self.nodes:
                if isinstance(node, MaltNode):
                    node.setup()
            for node in self.nodes:
                if isinstance(node, MaltNode):
                    node.update()
        except:
            import traceback
            traceback.print_exc()
        self.disable_updates = False

    def update(self):
        if self.disable_updates:
            return

        if self.get_pipeline_graph() is None:
            return

        self.disable_updates = True
        try:
            for link in self.links:
                try:
                    if (link.from_socket.array_size != link.to_socket.array_size or 
                        (link.from_socket.data_type != link.to_socket.data_type and
                        self.cast(link.from_socket.data_type, link.to_socket.data_type) is None)):
                        self.links.remove(link)
                except:
                    pass
            
            source = self.get_generated_source()
            source_dir = self.get_generated_source_dir()
            source_path = self.get_generated_source_path()
            import pathlib
            pathlib.Path(source_dir).mkdir(parents=True, exist_ok=True)
            with open(source_path,'w') as f:
                f.write(source)
            from BlenderMalt import MaltMaterial
            MaltMaterial.track_shader_changes()
        except:
            import traceback
            traceback.print_exc()
        self.disable_updates = False
        
        # Force a depsgraph update. 
        # Otherwise these will be outddated in scene_eval
        self.update_tag()

def setup_node_trees():
    graphs = MaltPipeline.get_bridge().graphs
    for name, graph in graphs.items():
        preload_menus(graph.structs, graph.functions)
    
    track_library_changes(force_update=True, disable_tree_updates=True)
    
    for tree in bpy.data.node_groups:
        if tree.bl_idname == 'MaltTree':
            tree.reload_nodes()
            tree.update()

__LIBRARIES = {}    
def get_libraries():
    return __LIBRARIES
def get_empty_library():
    return {
        'structs':{},
        'functions':{},
        'paths':[],
    }
__TIMESTAMP = time.time()

def track_library_changes(force_update=False, disable_tree_updates=False):
    if bpy.context.scene.render.engine != 'MALT' and force_update == False:
        return 1

    global __LIBRARIES
    global __TIMESTAMP
    start_time = time.time()

    #purge unused libraries
    new_dic = {}
    for tree in bpy.data.node_groups:
        if isinstance(tree, MaltTree):
            src_path = tree.get_library_path()
            if src_path:
                if src_path in __LIBRARIES:
                    new_dic[src_path] = __LIBRARIES[src_path]
                else:
                    new_dic[src_path] = None
    __LIBRARIES = new_dic

    needs_update = set()
    for path, library in __LIBRARIES.items():
        root_dir = os.path.dirname(path)
        if os.path.exists(path):
            if library is None:
                needs_update.add(path)
            else:
                for sub_path in library['paths']:
                    sub_path = os.path.join(root_dir, sub_path)
                    if os.path.exists(sub_path):
                        # Don't track individual files granularly since macros can completely change them
                        if os.stat(sub_path).st_mtime > __TIMESTAMP:
                            needs_update.add(path)
                            break
    
    if len(needs_update) > 0:
        results = MaltPipeline.get_bridge().reflect_source_libraries(needs_update)
        for path, reflection in results.items():
            __LIBRARIES[path] = reflection
            preload_menus(reflection['structs'], reflection['functions'])
        
        if disable_tree_updates == False:
            for tree in bpy.data.node_groups:
                if isinstance(tree, MaltTree):
                    src_path = tree.get_library_path()
                    if src_path and src_path in needs_update:
                        tree.update()
    
    __TIMESTAMP = start_time
    return 0.1



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
        #layout.prop(context.space_data.node_tree, 'generated_source')


def preload_menus(structs, functions):
    files = set()
    for name, struct in structs.items():
        files.add(struct['file'])
    for file in files:
        get_structs_menu(file)
    
    files = set()
    for name, function in functions.items():
        files.add(function['file'])
    for file in files:
        get_functions_menu(file)
        

def insert_node(layout, type, label, settings = {}):
    operator = layout.operator("node.add_node", text=label)
    operator.type = type
    operator.use_transform = True
    for name, value in settings.items():
        item = operator.settings.add()
        item.name = name
        item.value = value
    return operator

__FUNCTION_MENUES = {}

def get_functions_menu(file):
    global __FUNCTION_MENUES

    if file not in __FUNCTION_MENUES.keys():
        file_to_label = file.replace('\\', '/').replace('/', ' - ').replace('.glsl', '').replace('_',' ')
        class_name = 'MALT_MT_functions_' + str(len(__FUNCTION_MENUES))
        
        def draw(self, context):
            graph = get_pipeline_graph(context)
            if graph:
                library_functions = context.space_data.node_tree.get_library()['functions']
                for name, function in chain(graph.functions.items(), library_functions.items()):
                    if function['file'] == file:
                        insert_node(self.layout, "MaltFunctionNode", name.replace('_', ' '), settings={
                            'function_type' : repr(name)
                        })

        menu_type = type(class_name, (bpy.types.Menu,), {
            "bl_space_type": 'NODE_EDITOR',
            "bl_label": file_to_label,
            "draw": draw,
        })
        bpy.utils.register_class(menu_type)

        __FUNCTION_MENUES[file] = class_name
    
    return __FUNCTION_MENUES[file]

__STRUCT_MENUES = {}

def get_structs_menu(file):
    global __STRUCT_MENUES

    if file not in __STRUCT_MENUES:
        file_to_label = file.replace('\\', '/').replace('/', ' - ').replace('.glsl', '').replace('_',' ')
        class_name = 'MALT_MT_structs_' + str(len(__STRUCT_MENUES))

        def draw(self, context):
            graph = get_pipeline_graph(context)
            if graph:
                library_structs = context.space_data.node_tree.get_library()['structs']
                for name, struct in chain(graph.structs.items(), library_structs.items()):
                    if struct['file'] == file:
                        insert_node(self.layout, "MaltStructNode", name.replace('_', ' '), settings={
                            'struct_type' : repr(name)
                        })

        menu_type = type(class_name, (bpy.types.Menu,), {
            "bl_space_type": 'NODE_EDITOR',
            "bl_label": file_to_label,
            "draw": draw,
        })
        bpy.utils.register_class(menu_type)

        __STRUCT_MENUES[file] = class_name
    
    return __STRUCT_MENUES[file]


class MALT_MT_NodeFunctions(bpy.types.Menu):
    
    bl_label = "Malt Node Functions Menu"

    def draw(self, context):
        graph = get_pipeline_graph(context)
        if graph:
            files = set()
            library_functions = context.space_data.node_tree.get_library()['functions']
            for name, function in chain(library_functions.items(), graph.functions.items()):
                files.add(function['file'])
            for file in sorted(files):
                self.layout.menu(get_functions_menu(file))

class MALT_MT_NodeStructs(bpy.types.Menu):
    
    bl_label = "Malt Node Structs Menu"

    def draw(self, context):
        graph = get_pipeline_graph(context)
        if graph:
            files = set()
            library_structs = context.space_data.node_tree.get_library()['structs']
            for name, struct in chain(library_structs.items(), graph.structs.items()):
                files.add(struct['file'])
            for file in sorted(files):
                self.layout.menu(get_structs_menu(file))

class MALT_MT_NodeInputs(bpy.types.Menu):
    
    bl_label = "Malt Node Inputs Menu"

    def draw(self, context):
        graph = get_pipeline_graph(context)
        if graph:
            for name in sorted(graph.graph_IO):
                insert_node(self.layout, "MaltIONode", name + ' Input', settings={
                    'is_output' : repr(False),
                    'io_type' : repr(name),
            })

class MALT_MT_NodeOutputs(bpy.types.Menu):
    
    bl_label = "Malt Node Outputs Menu"

    def draw(self, context):
        graph = get_pipeline_graph(context)
        if graph:
            for name in sorted(graph.graph_IO):
                insert_node(self.layout, "MaltIONode", name + ' Ouput', settings={
                    'is_output' : repr(True),
                    'io_type' : repr(name),
            })

class MALT_MT_NodeOther(bpy.types.Menu):
    
    bl_label = "Malt Node Other Menu"

    def draw(self, context):
        graph = get_pipeline_graph(context)
        if graph:
            insert_node(self.layout, "MaltInlineNode", 'Inline Code')
            insert_node(self.layout, "MaltArrayIndexNode", 'Array Index')

def add_node_ui(self, context):
    if context.space_data.tree_type != 'MaltTree':
        return
    if context.space_data.node_tree is None:
        self.layout.label(text='No active node tree')
        return
    if context.space_data.node_tree.graph_type == '':
        self.layout.label(text='No graph type selected')
        return
    graph = get_pipeline_graph(context)
    if graph:
        self.layout.menu("MALT_MT_NodeFunctions", text='Functions')
        self.layout.menu("MALT_MT_NodeStructs", text='Structs')
        self.layout.menu("MALT_MT_NodeInputs", text='Inputs')
        self.layout.menu("MALT_MT_NodeOutputs", text='Outputs')
        self.layout.menu("MALT_MT_NodeOther", text='Other')

def node_header_ui(self, context):
    if context.space_data.tree_type != 'MaltTree' or context.space_data.node_tree is None:
        return
    #self.layout.use_property_split=True
    #self.layout.alignment = 'LEFT'
    self.layout.prop(context.space_data.node_tree, 'library_source',text='')
    self.layout.prop_search(context.space_data.node_tree, 'graph_type', context.scene.world.malt, 'graph_types',text='')
    #self.layout.prop(context.space_data.node_tree, 'edit_material',text='')

    
classes = (
    MaltTree,
    NODE_PT_MaltNodeTree,
    MALT_MT_NodeFunctions,
    MALT_MT_NodeStructs,
    MALT_MT_NodeInputs,
    MALT_MT_NodeOutputs,
    MALT_MT_NodeOther,
)

def foreach_node_module(callback):
    import importlib
    nodes_dir = os.path.join(os.path.dirname(__file__), 'Nodes')
    for name in os.listdir(nodes_dir):
        try:
            if name == '__pycache__':
                continue
            if name.endswith('.py'):
                name = name[:-3]
            module = importlib.import_module(f'BlenderMalt.MaltNodes.Nodes.{name}')
            #importlib.reload(module)
            callback(module)
        except ModuleNotFoundError:
            # Ignore it. The file or dir is not a python module
            pass
        except Exception:
            import traceback
            traceback.print_exc()

def register():
    for _class in classes: bpy.utils.register_class(_class)

    from BlenderMalt.MaltNodes import MaltSocket, MaltNode
    MaltSocket.register()
    MaltNode.register()

    foreach_node_module(lambda module : module.register())

    bpy.types.NODE_MT_add.append(add_node_ui)
    bpy.types.NODE_HT_header.append(node_header_ui)

    bpy.app.timers.register(track_library_changes, persistent=True)
    

def unregister():
    bpy.app.timers.unregister(track_library_changes)
    
    bpy.types.NODE_MT_add.remove(add_node_ui)
    bpy.types.NODE_HT_header.remove(node_header_ui)

    foreach_node_module(lambda module : module.unregister())
    
    from BlenderMalt.MaltNodes import MaltSocket, MaltNode
    MaltSocket.unregister()
    MaltNode.unregister()

    for _class in reversed(classes): bpy.utils.unregister_class(_class)


