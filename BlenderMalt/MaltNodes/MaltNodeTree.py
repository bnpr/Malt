import os, time
from Malt.SourceTranspiler import GLSLTranspiler, PythonTranspiler
import bpy
from BlenderMalt.MaltProperties import MaltPropertyGroup
from BlenderMalt import MaltPipeline
from BlenderMalt.MaltUtils import malt_path_setter, malt_path_getter

from BlenderMalt.MaltNodes.MaltNode import MaltNode

def get_pipeline_graph(context):
    if context is None or context.space_data is None or context.space_data.edit_tree is None:
        return None
    return context.space_data.edit_tree.get_pipeline_graph()

class MaltTree(bpy.types.NodeTree):

    bl_label = "Malt Node Tree"
    bl_icon = 'NODETREE'

    def get_copy(self):
        copy = self.copy()
        copy.subscribed = False
        copy.reload_nodes()
        copy.update_ext(force_update=True)
        return copy
    
    type : bpy.props.EnumProperty(name = 'Type', items = [("MALT", "Malt", "Malt")],
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT'
    
    def poll_material(self, material):
        return material.malt.shader_nodes is self
    
    def update_graph_type(self, context):
        self.is_group_type = self.graph_type.endswith(' (Group)')
        graph = self.get_pipeline_graph()
        if graph and graph.default_graph_path and len(self.nodes) == 0:
            blend_path, tree_name = graph.default_graph_path
            blend_path += '.blend'
            if tree_name not in bpy.data.node_groups:
                internal_dir = 'NodeTree'
                bpy.ops.wm.append(
                    filepath=os.path.join(blend_path, internal_dir, tree_name),
                    directory=os.path.join(blend_path, internal_dir),
                    filename=tree_name
                )
                bpy.data.node_groups[tree_name].reload_nodes()
            name = self.name
            copy = bpy.data.node_groups[tree_name].get_copy()
            self.user_remap(copy)
            bpy.data.node_groups.remove(self)
            copy.name = name
        else:
            self.reload_nodes()
            self.update_ext(force_update=True)
    
    graph_type: bpy.props.StringProperty(name='Type', update=update_graph_type,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    is_group_type : bpy.props.BoolProperty(default=False,
        options={'SKIP_SAVE','LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    #deprecated
    library_source : bpy.props.StringProperty(name="Local Library", subtype='FILE_PATH',
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'},
        set=malt_path_setter('library_source'), get=malt_path_getter('library_source'))

    disable_updates : bpy.props.BoolProperty(name="Disable Updates", default=False,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    malt_parameters : bpy.props.PointerProperty(type=MaltPropertyGroup,
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    subscribed : bpy.props.BoolProperty(name="Subscribed", default=False,
        options={'SKIP_SAVE','LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})
    
    links_hash : bpy.props.StringProperty(options={'SKIP_SAVE','LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'})

    def is_active(self):
        return self.get_pipeline_graph() is not None
    
    def is_group(self):
        return self.is_group_type
    
    def get_group_source_name(self):
        name = self.get_transpiler().get_source_name(self.name_full, prefix='').upper()
        return name

    def get_group_function(self, force_update=False):
        if force_update == False and self.get('group_function'):
            return self['group_function']
        parameters = []
        for node in self.nodes:
            if node.bl_idname == 'MaltIONode':
                sockets = node.inputs if node.is_output else node.outputs
                for socket in sockets:
                    parameters.append({
                        'meta': {
                            'label': socket.name,    
                        },
                        'name': socket.get_source_reference(),
                        'type': socket.data_type,
                        'size': socket.array_size,
                        'io': 'out' if node.is_output else 'in'
                    })
        parameter_signature = ', '.join([f"{p['io']} {p['type']} {p['name']}" for p in parameters])
        signature = f'void {self.get_group_source_name()}({parameter_signature})'
        self['group_function'] = {
            'meta': {},
            'name': self.get_group_source_name(),
            'type': 'void',
            'parameters': parameters,
            'signature': signature,
        }
        return self['group_function']
    
    def get_group_parameters(self, overrides, proxys):
        groups = []
        parameters = {}
        def get_groups(tree):
            for node in tree.nodes:
                if node.bl_idname == 'MaltGroupNode' and node.group is not None:
                    if node.group not in groups:
                        groups.append(node.group)
                        get_groups(node.group)
        get_groups(self)
        for group in groups:
            parameters.update(group.malt_parameters.get_parameters(overrides, proxys))
        return parameters

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
    
    #deprecated
    def get_library(self):
        library_path = self.get_library_path()
        if library_path:
            return get_libraries()[library_path]
        else:
            return get_empty_library()
    
    def get_full_library(self):
        #TODO: Cache
        graph = self.get_pipeline_graph()
        library = self.get_library()
        if library:
            result = get_empty_library()
            result['functions'].update(graph.functions)
            result['structs'].update(graph.structs)
            result['subcategories'].update(graph.subcategories)
            result['functions'].update(library['functions'])
            result['structs'].update(library['structs'])
            return result
        else:
            return {
                'functions' : graph.functions,
                'structs' : graph.structs,
                'subcategories' : graph.subcategories,
            }
    
    def get_pipeline_graph(self, graph_type=None):
        if graph_type is None: 
            graph_type = self.graph_type
        bridge = MaltPipeline.get_bridge()
        if bridge and graph_type in bridge.graphs:
            return bridge.graphs[graph_type]
        return None
    
    def get_unique_node_id(self, base_name):
        if 'NODE_NAMES' not in self.keys():
            self['NODE_NAMES'] = {}
        if base_name not in self['NODE_NAMES'].keys():
            self['NODE_NAMES'][base_name] = 1
        else:
            self['NODE_NAMES'][base_name] += 1
        return base_name + str(self['NODE_NAMES'][base_name])
    
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
                if hasattr(node, 'get_source_code'):
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
            if hasattr(node, 'get_source_global_parameters'):
                shader['GLOBAL'] += node.get_source_global_parameters(transpiler)
        if self.is_group():
            shader['INCLUDE GUARD'] = self.get_group_source_name() + '_GLSL'
        source = pipeline_graph.generate_source(shader)
        if self.is_group():
            source = source.replace('void NODE_GROUP_FUNCTION()', self.get_group_function()['signature'])
            source = source.replace('NODE_GROUP_FUNCTION', self.get_group_source_name())
        self['source'] = source
        return self['source']
    
    def reload_nodes(self):
        self.disable_updates = True
        try:
            for node in self.nodes:
                if hasattr(node, 'setup'):
                    node.setup()
            for node in self.nodes:
                if hasattr(node, 'update'):
                    node.update()
            self.get_group_function(force_update=True)
        except:
            import traceback
            traceback.print_exc()
        self.disable_updates = False
    
    def on_name_change(self, old_src_name):
        if self.is_group():
            new_src_name = self.get_group_source_name()
            for key in list(self.malt_parameters.get_rna().keys()):
                if old_src_name in key:
                    self.malt_parameters.rename_property(key, key.replace(old_src_name, new_src_name))
            bpy.msgbus.clear_by_owner(self)
            self.subscribed = False
        self.update_ext(force_update=True)

    def update(self):
        if self.is_active():
            self.update_ext()
    
    def update_ext(self, force_track_shader_changes=True, force_update=False):
        if self.disable_updates:
            return

        if self.get_pipeline_graph() is None:
            return
        
        if self.subscribed == False:
            bpy.msgbus.subscribe_rna(key=self.path_resolve('name', False),
                owner=self, args=(self.get_group_source_name(),), notify=lambda arg : self.on_name_change(arg))
            self.subscribed = True
        
        links_str = ''
        for link in self.links:
            try:
                b = link.to_socket
                a = b.get_linked(ignore_muted=False)
                links_str += str(a) + str(b)
            except:
                pass #Reroute Node
        links_hash = str(hash(links_str))
        if force_update == False and links_hash == self.links_hash:
            return
        self.links_hash = links_hash

        self.disable_updates = True
        try:
            for link in self.links:
                try:
                    b = link.to_socket
                    a = b.get_linked(ignore_muted=False)
                    if (a.array_size != b.array_size or 
                        (a.data_type != b.data_type and
                        self.cast(a.data_type, b.data_type) is None)):
                        link.is_muted = True
                    else:
                        link.is_muted = False
                except:
                    pass
            
            source = self.get_generated_source(force_update=True)
            source_dir = self.get_generated_source_dir()
            source_path = self.get_generated_source_path()
            import pathlib
            pathlib.Path(source_dir).mkdir(parents=True, exist_ok=True)
            with open(source_path,'w') as f:
                f.write(source)
            
            if force_track_shader_changes:
                if self.is_group():
                    from pathlib import Path
                    visited_trees = set()
                    def recompile_users(updated_tree):
                        visited_trees.add(updated_tree)
                        if updated_tree.is_group():
                            for tree in bpy.data.node_groups:
                                if tree.bl_idname == 'MaltTree' and tree not in visited_trees:
                                    for node in tree.nodes:
                                        if node.bl_idname == 'MaltGroupNode' and node.group is updated_tree:
                                            recompile_users(tree)
                                            break
                        else:
                            #Touch the file to force a recompilation
                            Path(updated_tree.get_generated_source_path()).touch()
                            return
                    recompile_users(self)
            
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
        preload_menus(graph.structs, graph.functions, graph)
    
    track_library_changes(force_update=True, is_initial_setup=True)
    
    for tree in bpy.data.node_groups:
        if tree.bl_idname == 'MaltTree' and tree.is_active():
            tree.reload_nodes()
    for tree in bpy.data.node_groups:
        if tree.bl_idname == 'MaltTree' and tree.is_active():
            tree.update_ext(force_track_shader_changes=False, force_update=True)
            
    from BlenderMalt import MaltMaterial
    MaltMaterial.track_shader_changes()

#SKIP_SAVE doesn't work
def manual_skip_save():
    for tree in bpy.data.node_groups:
        if tree.bl_idname == 'MaltTree':
            tree.subscribed = False
            tree.links_hash = ''
            for node in tree.nodes:
                if hasattr(node, 'subscribed'):
                    node.subscribed = False

__LIBRARIES = {}    
def get_libraries():
    return __LIBRARIES
def get_empty_library():
    return {
        'structs':{},
        'functions':{},
        'subcategories':{},
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
            if '(Group)' in name:
                continue
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
        if tree.bl_idname == 'MaltTree' and tree.is_active():
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
            if tree.bl_idname == 'MaltTree' and tree.is_active():
                src_path = tree.get_library_path()
                if tree.graph_type in updated_graphs or (src_path and src_path in needs_update):
                    tree.reload_nodes()
                    tree.update_ext(force_track_shader_changes=False, force_update=True)
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
    from collections import OrderedDict

    # Uses copied code from the <nodeitems_utils> module. Manual check for updates required.
    class MaltNodeItem(NodeItem):

        def __init__(self, nodetype, category, *, label=None, settings=None, poll=None, draw=None, item_params=None):
            if settings is None:
                settings = {}

            self.nodetype = nodetype
            self._label = f'{category} - {label}'
            self.button_label = label
            self.settings = settings
            self.poll = poll
            self.item_params = item_params
            
            def draw_default(self, layout, _context):
                props = layout.operator("node.add_node", text=self.button_label, text_ctxt=self.translation_context)
                props.type = self.nodetype
                props.use_transform = True

                for setting in self.settings.items():
                    ops = props.settings.add()
                    ops.name = setting[0]
                    ops.value = setting[1]

            self.draw = staticmethod(draw) if draw else staticmethod(draw_default)
    
    class MaltSearchMenuItem(MaltNodeItem):

        def __init__(self, nodetype, category, *, label=None, settings=None, poll=None):
            def draw_nothing(self, layout, _context):
                return
            super().__init__(nodetype, category, label=label, settings=settings, poll=poll, draw=draw_nothing)


    category_id = f'MALT{graph.name.upper()}'

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
        'Internal' : [],
    }

    for name in graph.graph_io:
        label = name.replace('_',' ')
        categories['Node Tree'].append(NodeItem('MaltIONode', label=f'{label} Input', settings=OrderedDict({
            'name' : repr(f'{label} Input'),
            'is_output' : repr(False),
            'io_type' : repr(name),
        })))
        categories['Node Tree'].append(NodeItem('MaltIONode', label=f'{label} Output', settings=OrderedDict({
            'name' : repr(f'{label} Output'),
            'is_output' : repr(True),
            'io_type' : repr(name),
        })))
    
    if graph.language == 'GLSL':
        categories['Other'].append(NodeItem('MaltInlineNode', label='Inline Code', settings={
            'name' : repr('Inline Code')
        }))
        categories['Other'].append(NodeItem('MaltArrayIndexNode', label='Array Element', settings={
            'name' : repr('Array Element')
        }))
        categories['Other'].append(NodeItem('MaltGroupNode', label='Node Group', settings={
            'name' : repr('Node Group')
        }))

    subcategories = set()
    
    def add_to_category(dic, node_type):
        for k,v in dic.items():
            if (is_internal := v['meta'].get('internal')):
                category = 'Internal'
            else:
                category = v['meta'].get('category')
            if category is None:
                category = v['file'].replace('\\', '/').replace('/', ' - ').replace('.glsl', '').replace('_',' ')
            if category not in categories:
                categories[category] = []

            _node_type = node_type
            label = v['meta'].get('label', v['name'])
            subcategory = v['meta'].get('subcategory')
            
            settings = OrderedDict({
                'name': repr(label),
                'malt_label': repr(label)
            })
            
            if subcategory and not is_internal:
                _node_type = 'MaltFunctionSubCategoryNode'
                label = subcategory
                settings.update({
                    'name' : repr(label),
                    'malt_label': repr(label),
                    'subcategory': repr(subcategory),
                    'function_enum': repr(k),
                })
                func_label = v['meta']['label']

                def draw_subcategory_item(self: MaltNodeItem, layout, _context):
                    props = layout.operator('node.add_subcategory_node', text=self.button_label)
                    props.settings = repr(self.settings)
                
                #add subcategory functions to the search menu but not to the regular menus
                categories['Node Tree'].append(MaltSearchMenuItem(_node_type, category, label=f'{subcategory}: {func_label}', settings=settings))
                if subcategory in subcategories:
                    continue
                subcategories.add(subcategory)
                node_item = MaltNodeItem(_node_type, category, label=label, settings=settings, draw=draw_subcategory_item)
            else:
                if node_type == 'MaltFunctionNode':
                    settings['function_type'] = repr(k)
                elif node_type == 'MaltStructNode':
                    settings['struct_type'] = repr(k)
                node_item = MaltNodeItem(_node_type, category, label=label, settings=settings)
            
            categories[category].append(node_item)

    add_to_category(functions, 'MaltFunctionNode')
    add_to_category(structs, 'MaltStructNode')

    def poll(cls, context):
        tree = context.space_data.edit_tree
        return tree and tree.bl_idname == 'MaltTree' and tree.graph_type == graph.name

    def poll_internal(cls, context):
        preferences = bpy.context.preferences.addons['BlenderMalt'].preferences
        return poll(cls, context) and preferences.show_internal_nodes

    category_type = type(category_id, (NodeCategory,), 
    {
        'poll': classmethod(poll),
    })
    category_internal_type = type(f'{category_id}_INTERNAL', (category_type,),
    {
        'poll': classmethod(poll_internal),
    })

    from BlenderMalt import _PLUGINS
    for plugin in _PLUGINS:
        try:
            for category, nodeitems in plugin.blendermalt_register_nodeitems(MaltNodeItem).items():
                if category not in categories.keys():
                    categories[category] = []
                categories[category].extend(nodeitems)
        except:
            import traceback
            traceback.print_exc()
            
    category_list = []
    for category_name, node_items in categories.items():
        if not len(node_items):
            continue
        bl_id = f'{category_id}_{category_name}'
        bl_id = ''.join(c for c in bl_id if c.isalnum())
        if len(bl_id) > 64:
            bl_id = bl_id[:64]
        if category_name == 'Internal':
            category_list.append(category_internal_type(bl_id, category_name, items=node_items))
        else:
            category_list.append(category_type(bl_id, category_name, items=node_items))

    register_node_categories(category_id, category_list)


def node_header_ui(self, context):
    node_tree = context.space_data.edit_tree
    if context.space_data.tree_type != 'MaltTree' or node_tree is None:
        return
    def duplicate():
        context.space_data.node_tree = node_tree.get_copy()
    self.layout.operator('wm.malt_callback', text='', icon='DUPLICATE').callback.set(duplicate, 'Duplicate')
    def recompile():
        node_tree.reload_nodes()
        node_tree.update_ext(force_update=True)
    self.layout.operator("wm.malt_callback", text='', icon='FILE_REFRESH').callback.set(recompile, 'Recompile')
    self.layout.prop_search(node_tree, 'graph_type', context.scene.world.malt, 'graph_types',text='')
    

def get_node_spaces(context):
    spaces = []
    locked_spaces = []
    for window in context.window_manager.windows:
        for area in window.screen.areas:
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


def active_material_update(dummy=None):
    try:
        material = bpy.context.object.active_material
        node_tree = material.malt.shader_nodes
    except:
        node_tree = None
    if node_tree:
        spaces, locked_spaces = get_node_spaces(bpy.context)
        for space in spaces:
            if space.node_tree is None or space.node_tree.graph_type == 'Mesh':
                space.node_tree = node_tree
                return


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
    active_material_update()

@bpy.app.handlers.persistent
def load_post(dummy=None):
    #msgbus subscriptions can't be persistent across file loads :(
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "active_material_index"),
        owner=__msgbus_owner,
        args=(None,),
        notify=active_material_update
    )

classes = [
    MaltTree,
    NODE_PT_MaltNodeTree,
]
__msgbus_owner = object()


def register():
    for _class in classes: bpy.utils.register_class(_class)

    bpy.types.NODE_HT_header.append(node_header_ui)

    bpy.app.timers.register(track_library_changes, persistent=True)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update)
    bpy.app.handlers.load_post.append(load_post)
    

def unregister():
    bpy.msgbus.clear_by_owner(__msgbus_owner)

    bpy.app.handlers.load_post.remove(load_post)
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update)
    bpy.app.timers.unregister(track_library_changes)
    
    bpy.types.NODE_HT_header.remove(node_header_ui)

    for _class in reversed(classes): bpy.utils.unregister_class(_class)