import os, time
from typing import Union
from Malt.SourceTranspiler import GLSLTranspiler, PythonTranspiler
import bpy
from BlenderMalt.MaltProperties import MaltPropertyGroup
from BlenderMalt import MaltPipeline
from BlenderMalt.MaltUtils import malt_path_setter, malt_path_getter

from . MaltNode import MaltNode

class NodeTreePreview(bpy.types.PropertyGroup):

    # Name of the node used as a preview
    node_name: bpy.props.StringProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    # Socket name and index are stored to provide fallbacks
    socket_name: bpy.props.StringProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    socket_index: bpy.props.IntProperty(
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    @property
    def node_tree(self) -> 'MaltTree':
        return self.id_data

    def is_socket_valid(self, socket: bpy.types.NodeSocket) -> bool:
        return (
            socket.node in self.node_tree.nodes.values()
            and not socket.is_output
        )
    
    def get_node(self) -> Union[bpy.types.Node, None]:
        return self.node_tree.nodes.get(self.node_name, None)
    
    def get_socket_ex(self) -> tuple[Union[bpy.types.NodeSocket, None], Union[str, int]]:
        '''Gets the stored socket. Because all references have to be strings and ints, the validity of the references have to be checked first.'''
        if (node := self.get_node()) == None:
            return None, ''
        if self.socket_name in node.inputs.keys():
            return node.inputs[self.socket_name], self.socket_name
        elif len(node.inputs) > self.socket_index:
            return node.inputs[self.socket_index], self.socket_index
        else:
            return None, ''
    
    def get_socket(self) -> Union[bpy.types.NodeSocket, None]:
        return self.get_socket_ex()[0]

    @staticmethod
    def _get_visible_node_sockets(node: bpy.types.Node, get_outputs: bool = False) -> list[bpy.types.NodeSocket]:
        front = node.outputs if get_outputs else node.inputs
        return [s for s in front.values() if s.enabled and (not s.hide or len(s.links))]

    def set_socket(self, socket: bpy.types.NodeSocket) -> bool:
        '''Store the given socket as the preview.'''
        if not self.is_socket_valid(socket):
            return False

        self.node_name = socket.node.name
        self.socket_name = socket.name
        self.socket_index = next(i for i, s in enumerate(self._get_visible_node_sockets(socket.node, get_outputs=False)) if s == socket)
        return True
    
    def reset_socket_from_node(self, node: bpy.types.Node) -> bool:
        '''Store a socket as the preview of the given node. If a socket of that node is already the preview, cycle through the sockets, otherwise use the first socket.'''
        node_inputs = self._get_visible_node_sockets(node, get_outputs=False)
        if (input_count := len(node_inputs)) < 1:
            return False
        old_socket = self.get_socket()
        if not self.get_node() == node or old_socket == None:
            return self.set_socket(node_inputs[0])
        else:
            old_index = next(i for i, s in enumerate(node_inputs) if s == old_socket)
            return self.set_socket(node_inputs[(old_index + 1) % input_count])
    
    def connect_socket(self, socket: bpy.types.NodeSocket) -> bool:
        preview_socket = self.get_socket()
        if not preview_socket or preview_socket.node == socket.node or not socket.is_output:
            return False
        self.node_tree.links.new(socket, preview_socket)
    
    def reconnect_node(self, node: bpy.types.Node) -> bool:
        '''Connect a node to the preview socket by cycling through its sockets.'''
        preview_socket = self.get_socket()
        node_outputs = self._get_visible_node_sockets(node, get_outputs=True)
        if not preview_socket or preview_socket.node == node or len(node_outputs) < 1:
            return False
        try: # Node is already connected to preview socket. Connect next socket
            previous_socket = next(
                link.from_socket 
                for link in preview_socket.links 
                if link.from_socket.node == node and link.from_socket in node_outputs)
            previous_index = next(i for i, s in enumerate(node_outputs) if s == previous_socket)
            new_socket = node_outputs[(previous_index + 1) % len(node_outputs)]
            self.connect_socket(new_socket)
        except StopIteration: # When the node is not already connected, use the first socket
            self.connect_socket(node_outputs[0])
        return True

def get_pipeline_graph(context):
    if context is None or context.space_data is None or context.space_data.edit_tree is None:
        return None
    return context.space_data.edit_tree.get_pipeline_graph()

class MaltTree(bpy.types.NodeTree):

    bl_label = "Malt Node Tree"
    bl_icon = 'NODETREE'

    type : bpy.props.EnumProperty(name = 'Type', items = [("MALT", "Malt", "Malt")],
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT'
    
    def poll_material(self, material):
        return material.malt.shader_nodes is self
    
    graph_type: bpy.props.StringProperty(name='Type',
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    library_source : bpy.props.StringProperty(name="Local Library", subtype='FILE_PATH',
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'},
        set=malt_path_setter('library_source'), get=malt_path_getter('library_source'))

    disable_updates : bpy.props.BoolProperty(name="Disable Updates", default=False,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    malt_parameters : bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    subscribed : bpy.props.BoolProperty(name="Subscribed", default=False,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    tree_preview : bpy.props.PointerProperty(type=NodeTreePreview, name="Node Tree Preview",
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    def is_active(self):
        return self.get_pipeline_graph() is not None

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
    
    def get_pipeline_graph(self, graph_type=None):
        if graph_type is None: 
            graph_type = self.graph_type
        bridge = MaltPipeline.get_bridge()
        if bridge and graph_type in bridge.graphs:
            return bridge.graphs[graph_type]
        return None
    
    def get_custom_io(self, io_type):
        params = []
        for node in self.nodes:
            if node.bl_idname == 'MaltIONode' and node.io_type == io_type:
                io = 'out' if node.is_output else 'in'
                for parameter in node.get_custom_parameters():
                    params.append({
                        'name': parameter.name,
                        'type': 'Texture', #TODO
                        'size': 0,
                        'io': io,
                    })
        return params
    
    def cast(self, from_type, to_type):
        cast_function = f'{to_type}_from_{from_type}'
        lib = self.get_full_library()
        for function in lib['functions'].values():
            if function['name'] == cast_function and len(function['parameters']) == 1:
                #TODO: If more than 1 parameter, check if they have default values?
                return function['name']
        return None
    
    def get_struct_type(self, struct_type):
        lib = self.get_full_library()
        if struct_type in lib['structs']:
            return lib['structs'][struct_type]
        return None
    
    def get_generated_source_dir(self):
        import os, tempfile
        base_path = tempfile.gettempdir()
        if bpy.context.blend_data.is_saved:
            base_path = bpy.path.abspath('//')
        return os.path.join(base_path,'.malt-autogenerated')

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
    
    def get_generated_source(self, force_update=False):
        if force_update == False and self.get('source'):
            return self['source']

        output_nodes = []
        linked_nodes = []
        
        pipeline_graph = self.get_pipeline_graph()
        if pipeline_graph:
            for node in self.nodes:
                #TODO: MaltNode.is_result()
                if node.bl_idname == 'MaltIONode' and node.is_output:
                    output_nodes.append(node)
                    linked_nodes.append(node)
        
        def add_node_inputs(node, list, io_type):
            for input in node.inputs:
                if input.get_linked():
                    new_node = input.get_linked().node
                    if new_node.bl_idname == 'MaltIONode' and new_node.io_type != io_type:
                        input.links[0].is_muted = True
                        continue
                    if new_node not in list:
                        add_node_inputs(new_node, list, io_type)
                        list.append(new_node)
                    if new_node not in linked_nodes:
                        linked_nodes.append(new_node)
        
        transpiler = self.get_transpiler()
        def get_source(output):
            nodes = []
            add_node_inputs(output, nodes, output.io_type)
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
        self['source'] = pipeline_graph.generate_source(shader)
        return self['source']
    
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
        if self.is_active():
            self.update_ext()
    
    def update_ext(self, force_track_shader_changes=True):
        if self.disable_updates:
            return

        if self.get_pipeline_graph() is None:
            return
        
        if self.subscribed == False:
            bpy.msgbus.subscribe_rna(key=self.path_resolve('name', False),
                owner=self, args=(None,), notify=lambda _ : self.update())
            self.subscribed = True

        self.disable_updates = True
        try:
            for link in self.links:
                try:
                    b = link.to_socket
                    a = b.get_linked()
                    if (a.array_size != b.array_size or 
                        (a.data_type != b.data_type and
                        self.cast(a.data_type, b.data_type) is None)):
                        link.is_muted = True
                except:
                    link.is_muted = False
            
            source = self.get_generated_source(force_update=True)
            source_dir = self.get_generated_source_dir()
            source_path = self.get_generated_source_path()
            import pathlib
            pathlib.Path(source_dir).mkdir(parents=True, exist_ok=True)
            with open(source_path,'w') as f:
                f.write(source)
            if force_track_shader_changes:
                from BlenderMalt import MaltMaterial
                MaltMaterial.track_shader_changes()
        except:
            import traceback
            traceback.print_exc()
        self.disable_updates = False
        
        # Force a depsgraph update. 
        # Otherwise these will be outddated in scene_eval
        self.update_tag()


def reset_subscriptions():
    for tree in bpy.data.node_groups:
        if tree.bl_idname == 'MaltTree':
            tree.subscribed = False
            for node in tree.nodes:
                if isinstance(node, MaltNode):
                    node.subscribed = False

def setup_node_trees():
    graphs = MaltPipeline.get_bridge().graphs

    for name, graph in graphs.items():
        preload_menus(graph.structs, graph.functions, graph)
    
    track_library_changes(force_update=True, is_initial_setup=True)
    
    for tree in bpy.data.node_groups:
        if tree.bl_idname == 'MaltTree' and tree.is_active():
            tree.reload_nodes()
            tree.update_ext(force_track_shader_changes=False)
    from BlenderMalt import MaltMaterial
    MaltMaterial.track_shader_changes()

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

def track_library_changes(force_update=False, is_initial_setup=False):
    from BlenderMalt import MaltPipeline
    if MaltPipeline.is_malt_active() == False and force_update == False:
        return 1
    
    bridge = MaltPipeline.get_bridge()
    graphs = MaltPipeline.get_bridge().graphs
    updated_graphs = []
    if is_initial_setup == False:
        for name, graph in graphs.items():
            if graph.needs_reload():
                updated_graphs.append(name)
        if len(updated_graphs) > 0:        
            bridge.reload_graphs(updated_graphs)
            for graph_name in updated_graphs:
                graph = graphs[graph_name]
                preload_menus(graph.structs, graph.functions, graphs[graph_name])

    global __LIBRARIES
    global __TIMESTAMP
    start_time = time.time()

    #purge unused libraries
    new_dic = {}
    for tree in bpy.data.node_groups:
        if isinstance(tree, MaltTree) and tree.is_active():
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
        
    if is_initial_setup == False and max(len(needs_update), len(updated_graphs)) > 0:
        for tree in bpy.data.node_groups:
            if isinstance(tree, MaltTree) and tree.is_active():
                src_path = tree.get_library_path()
                if tree.graph_type in updated_graphs or (src_path and src_path in needs_update):
                    tree.reload_nodes()
                    tree.update_ext(force_track_shader_changes=False)
        from BlenderMalt import MaltMaterial
        MaltMaterial.track_shader_changes()
    
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


def preload_menus(structs, functions, graph=None):
    if graph is None:
        return

    from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories

    class SubCategoryNodeItem(NodeItem):

        def __init__(self, node_idname, label='', settings: dict={}, poll=None):
            self.node_idname = node_idname
            self.subcategory = settings['subcategory']
            self.function_enum = settings['function_enum']
            self.node_name = settings['name']
            self.button_label = label
            self.poll=poll

        @staticmethod
        def draw(self:'SubCategoryNodeItem', layout, _context):
            props = layout.operator(NODE_OT_MaltAddSubcategoryNode.bl_idname, text = self.button_label)
            props.subcategory = self.subcategory
            props.function_enum = self.function_enum
            props.name = self.node_name

    category_id = f'BLENDERMALT_{graph.name.upper()}'

    try:
        unregister_node_categories(category_id) # you could also check the hidden <nodeitems_utils._node_categories>
    except:
        pass #First run

    categories = {
        'Input' : [],
        'Parameters' : [],
        'Math' : [],
        'Vector' : [],
        'Color' : [],
        'Texturing' : [],
        'Shading' : [],
        'Filter' : [],
        'Other' : [],
        'Node Tree' : [],
    }

    for name in graph.graph_io:
        label = name.replace('_',' ')
        categories['Node Tree'].append(NodeItem('MaltIONode', label=f'{label} Input', settings={
            'is_output' : repr(False),
            'io_type' : repr(name),
            'name' : repr(f'{label} Input'),
        }))
        categories['Node Tree'].append(NodeItem('MaltIONode', label=f'{label} Output', settings={
            'is_output' : repr(True),
            'io_type' : repr(name),
            'name' : repr(f'{label} Output'),
        }))
    
    categories['Other'].append(NodeItem('MaltInlineNode', label='Inline Code', settings={
        'name' : repr('Inline Code')
    }))
    categories['Other'].append(NodeItem('MaltArrayIndexNode', label='Array Element', settings={
        'name' : repr('Array Element')
    }))

    subcategories = set()
    
    def add_to_category(dic, node_type):
        for k,v in dic.items():
            if v['meta'].get('internal'):
                continue
            category = v['meta'].get('category')
            if category is None:
                category = v['file'].replace('\\', '/').replace('/', ' - ').replace('.glsl', '').replace('_',' ')
            if category not in categories:
                categories[category] = []

            _node_type = node_type
            label = v['meta'].get('label', v['name'])
            
            settings = {}
            if node_type == 'MaltFunctionNode':
                settings['function_type'] = repr(k)
            elif node_type == 'MaltStructNode':
                settings['struct_type'] = repr(k)
            subcategory = v['meta'].get('subcategory')
            
            if subcategory:
                if subcategory in subcategories:
                    continue
                subcategories.add(subcategory)
                _node_type = 'MaltFunctionSubCategoryNode'
                label = subcategory
                node_item = SubCategoryNodeItem(_node_type, label=label, settings={
                    'name' : label,
                    'subcategory' : subcategory,
                    'function_enum' : k,
                })
            else:
                settings['name'] = repr(label)
                from collections import OrderedDict
                settings = OrderedDict(settings)
                # name must be set first for labels to work correctly
                settings.move_to_end('name', last=False)
                node_item = NodeItem(_node_type, label=label, settings=settings)
            categories[category].append(node_item)

    add_to_category(functions, 'MaltFunctionNode')
    add_to_category(structs, 'MaltStructNode')

    @classmethod
    def poll(cls, context):
        tree = context.space_data.edit_tree
        return tree and tree.bl_idname == 'MaltTree' and tree.graph_type == graph.name
    
    category_type = type(category_id, (NodeCategory,), 
    {
        'poll': poll,
    })
            
    category_list = []
    for category_name, node_items in categories.items():
        if not len(node_items):
            continue
        bl_id = f'{category_id}_{category_name}'
        bl_id = ''.join(c for c in bl_id if c.isalnum())
        if len(bl_id) > 64:
            bl_id = bl_id[:64]
        category_list.append(category_type(bl_id, category_name, items=node_items))

    register_node_categories(category_id, category_list)


def node_header_ui(self, context):
    node_tree = context.space_data.edit_tree
    if context.space_data.tree_type != 'MaltTree' or node_tree is None:
        return
    def duplicate():
        context.space_data.node_tree = node_tree.copy()
    self.layout.operator('wm.malt_callback', text='', icon='DUPLICATE').callback.set(duplicate, 'Duplicate')
    def recompile():
        node_tree.update()
    self.layout.operator("wm.malt_callback", text='', icon='FILE_REFRESH').callback.set(recompile, 'Recompile')
    self.layout.prop(node_tree, 'library_source',text='')
    self.layout.prop_search(node_tree, 'graph_type', context.scene.world.malt, 'graph_types',text='')

@bpy.app.handlers.persistent
def depsgraph_update(scene, depsgraph):
    # Show the active material node tree in the Node Editor
    from BlenderMalt import MaltPipeline
    if MaltPipeline.is_malt_active() == False:
        return
    scene_updated = False
    for deps_update in depsgraph.updates:
        if isinstance(deps_update.id, bpy.types.Scene):
            scene_updated = True
    if scene_updated == False:
        return
    node_tree = None
    try:
        material = bpy.context.object.active_material
        node_tree = material.malt.shader_nodes
    except:
        pass
    if node_tree:
        spaces, locked_spaces = get_node_spaces(bpy.context)
        for space in spaces:
            if space.node_tree.graph_type == 'Mesh':
                space.node_tree = node_tree
                return

def get_node_spaces(context):
    spaces = []
    locked_spaces = []
    for area in context.screen.areas:
        if area.type == 'NODE_EDITOR':
            for space in area.spaces:
                if space.type == 'NODE_EDITOR' and space.tree_type == 'MaltTree':
                    if space.pin == False or space.node_tree is None:
                        spaces.append(space)
                    else:
                        locked_spaces.append(space)
    return spaces, locked_spaces

def set_node_tree(context, node_tree, node = None):
    if context.space_data.type == 'NODE_EDITOR' and context.area.ui_type == 'MaltTree':
        context.space_data.path.append(node_tree, node = node)
    else:
        spaces, locked_spaces = get_node_spaces(context)
        if len(spaces) > 0:
            spaces[0].node_tree = node_tree
        elif len(locked_spaces) > 0:
            locked_spaces[0].node_tree = node_tree

def is_malt_tree_context(context: bpy.types.Context) -> bool:
    return context.area.ui_type == 'MaltTree' and context.space_data.type == 'NODE_EDITOR' and context.space_data.edit_tree

class OT_MaltEditNodeTree(bpy.types.Operator):
    bl_idname = 'wm.malt_edit_node_tree'
    bl_label = 'Edit Node Tree'

    @classmethod
    def poll( cls, context ):
        return is_malt_tree_context(context)
            
    def execute( self, context ):
        node = context.active_node
        space_path = context.space_data.path
        node_tree = None
        if node and hasattr(node, 'get_pass_node_tree'):
            node_tree = node.get_pass_node_tree()
        if node_tree:
            space_path.append(node_tree, node = node)
        else:
            space_path.pop()
        return {'FINISHED'}

class OT_MaltSetTreePreview(bpy.types.Operator):
    bl_idname = 'wm.malt_set_tree_preview'
    bl_label = 'Set Tree Preview'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return is_malt_tree_context(context)
    
    def execute(self, context):
        node_tree: MaltTree = context.space_data.edit_tree
        node = context.active_node
        if not node:
            return {'CANCELLED'}
        node_tree.tree_preview.reset_socket_from_node(node)
        context.area.tag_redraw()
        return {'FINISHED'}

class OT_MaltConnectTreePreview(bpy.types.Operator):
    bl_idname = 'wm.malt_connect_tree_preview'
    bl_label = 'Connect To Tree Preview'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return is_malt_tree_context(context)
    
    def execute(self, context):
        node_tree: MaltTree = context.space_data.edit_tree
        node = context.active_node
        if not node:
            return {'CANCELLED'}
        tp: NodeTreePreview = node_tree.tree_preview
        tp.reconnect_node(node)
        context.area.tag_redraw()
        return {'FINISHED'}

import string

class NODE_OT_MaltAddSubcategoryNode(bpy.types.Operator):
    bl_idname = 'node.malt_add_subcategory_node'
    bl_label = 'Add Subcategory Node'
    bl_options = {'UNDO'}

    subcategory : bpy.props.StringProperty()
    function_enum : bpy.props.StringProperty()
    name : bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return is_malt_tree_context(context)
    
    @staticmethod
    def get_region_mouse(sd: bpy.types.SpaceNodeEditor) -> tuple[float, float]:
        return sd.cursor_location

    def add_node(self, node_tree:MaltTree) -> bpy.types.Node:
        node = node_tree.nodes.new('MaltFunctionSubCategoryNode')
        node_tree.disable_updates = True
        node.name = self.name
        node.subcategory = self.subcategory
        node.function_enum = self.function_enum
        return node

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        self.node_tree: MaltTree = context.space_data.edit_tree
        self.node_tree.disable_updates = True

        try:
            self.node: MaltNode = self.add_node(self.node_tree)
            self.disable_malt_updates(True)
            self.node.location = self.get_region_mouse(context.space_data)
            self.disable_malt_updates(False)

            self.function_enums:list[tuple[str,str,str]] = self.node.get_function_enums(context)
        except:
            import traceback
            traceback.print_exc()
            return self.cancel(context)
        
        #Call the transform operator to access auto connection
        for n in self.node_tree.nodes:
            n.select = False
        self.node.select = True

        bpy.ops.transform.transform('INVOKE_DEFAULT')

        self.finish_modal = False
        
        wm = context.window_manager
        wm.modal_handler_add(self)
        return{'RUNNING_MODAL'}
    
    def disable_malt_updates(self, disable):
        self.node.disable_updates = disable
        self.node_tree.disable_updates = disable
    
    def schedule_execute(self) -> set[str]:
        self.finish_modal = True
        return {'PASS_THROUGH'}

    def cycle_function_enums(self, letter: str, cycle_forward: bool) -> None:
        letter = letter.lower()
        enum_subset = [enum for enum in self.function_enums if enum[1].lower().startswith(letter)]
        if not len(enum_subset):
            return #do nothing if there are no possible function_enums with the given letter

        new_function_enum = enum_subset[0 if cycle_forward else -1][0]
        if self.node.function_enum in (enum[0] for enum in enum_subset):
            old_index = next(i for i, enum in enumerate(enum_subset) if enum[0] == self.node.function_enum)
            offset = 1 if cycle_forward else -1
            new_function_enum = enum_subset[(old_index + offset) % len(enum_subset)][0]
        
        self.disable_malt_updates(True)
        self.node.function_enum = new_function_enum
        self.node.setup_width()
        self.disable_malt_updates(False)

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):

        if self.finish_modal:
            return self.execute(context)

        if event.type in ['LEFTMOUSE', 'RET', 'SPACE']:
            self.schedule_execute()
        if event.type in ['ESC', 'RIGHTMOUSE'] and event.value == 'RELEASE':
            return self.cancel(context)
        if event.type in string.ascii_uppercase and event.value == 'PRESS':
            self.cycle_function_enums(event.type, not event.shift)
            return{'RUNNING_MODAL'}
        
        return{'PASS_THROUGH'}

    def execute(self, context: bpy.types.Context):
        if not self.options.is_invoke:
            self.node_tree: MaltTree = context.space_data.edit_tree
            self.node_tree.disable_updates = True
            self.add_node(self.node_tree)
        self.node_tree.disable_updates = False
        return{'FINISHED'}
    
    def cancel(self, context):
        if self.node:
            context.space_data.edit_tree.nodes.remove(self.node)
        return{'CANCELLED'}
    
keymaps = []
def register_node_tree_shortcuts():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name = 'Node Editor', space_type = 'NODE_EDITOR')
        kmi = km.keymap_items.new(OT_MaltEditNodeTree.bl_idname, type = 'TAB', value = 'PRESS')
        keymaps.append((km, kmi))

        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new(OT_MaltSetTreePreview.bl_idname, type ='P', value ='PRESS', shift=True )
        keymaps.append((km, kmi))

        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new(OT_MaltConnectTreePreview.bl_idname, type='P', value='PRESS', shift=False)
        keymaps.append((km, kmi))

classes = [
    NodeTreePreview,
    MaltTree,
    NODE_PT_MaltNodeTree,
    OT_MaltEditNodeTree,
    NODE_OT_MaltAddSubcategoryNode,
    OT_MaltSetTreePreview,
    OT_MaltConnectTreePreview,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)

    bpy.types.NODE_HT_header.append(node_header_ui)

    bpy.app.timers.register(track_library_changes, persistent=True)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update)

    def context_path_ui_callback():
        import blf
        font_id = 0
        context = bpy.context
        space = context.space_data
        if not is_malt_tree_context(context):
            return
        if not space.overlay.show_context_path:
            return
        path = space.path
        text = ' > '.join(x.node_tree.name for x in path)
        preferences = context.preferences
        ui_scale = preferences.view.ui_scale
        dpi = preferences.system.dpi
        size = preferences.ui_styles[0].widget.points * ui_scale
        color = preferences.themes[0].node_editor.space.text
        blf.size(font_id, size, dpi)
        blf.position(font_id, 10, 10, 0)
        blf.color(font_id, *color, 1)
        blf.draw(font_id, text)
    
    def tree_preview_ui_callback():
        import blf
        font_id = 0
        context = bpy.context
        space:bpy.types.SpaceNodeEditor = context.space_data
        if not is_malt_tree_context(context):
            return
        node_tree:MaltTree = space.edit_tree
        tp:NodeTreePreview = node_tree.tree_preview
        socket, identifier = tp.get_socket_ex()
        if socket == None:
            return
        node = socket.node
        text = f'Preview: {repr(identifier)}'
        preferences = context.preferences
        size = preferences.ui_styles[0].widget_label.points
        ui_scale = preferences.view.ui_scale

        blf.size(0, size * ui_scale, 72)
        blf.position(font_id, node.location[0] * ui_scale, node.location[1] * ui_scale + 2, 0)
        blf.color(font_id, 1,1,1,1)
        blf.draw(font_id, text)

    global CONTEXT_PATH_DRAW_HANDLER, TREE_PREVIEW_DRAW_HANDLER
    CONTEXT_PATH_DRAW_HANDLER = bpy.types.SpaceNodeEditor.draw_handler_add(context_path_ui_callback, (), 'WINDOW', 'POST_PIXEL')
    TREE_PREVIEW_DRAW_HANDLER = bpy.types.SpaceNodeEditor.draw_handler_add(tree_preview_ui_callback, (), 'WINDOW', 'POST_VIEW')

    register_node_tree_shortcuts()

def unregister():

    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
        keymaps.clear()
    
    global CONTEXT_PATH_DRAW_HANDLER, TREE_PREVIEW_DRAW_HANDLER
    bpy.types.SpaceNodeEditor.draw_handler_remove(CONTEXT_PATH_DRAW_HANDLER, 'WINDOW')
    bpy.types.SpaceNodeEditor.draw_handler_remove(TREE_PREVIEW_DRAW_HANDLER, 'WINDOW')

    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update)
    bpy.app.timers.unregister(track_library_changes)
    
    bpy.types.NODE_HT_header.remove(node_header_ui)

    for _class in reversed(classes): bpy.utils.unregister_class(_class)


