import bpy
import string
from typing import Union
from bpy.types import NodeTree
from bpy.props import PointerProperty
from . MaltNodeTree import MaltTree

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
    def node_tree(self) -> NodeTree:
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
        node_tree: NodeTree = context.space_data.edit_tree
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
        node_tree: NodeTree = context.space_data.edit_tree
        node = context.active_node
        if not node:
            return {'CANCELLED'}
        tp: NodeTreePreview = node_tree.tree_preview
        tp.reconnect_node(node)
        context.area.tag_redraw()
        return {'FINISHED'}

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

    def add_node(self, node_tree):
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
            self.node = self.add_node(self.node_tree)
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

classes = [
    NodeTreePreview,
    OT_MaltEditNodeTree,
    OT_MaltSetTreePreview,
    OT_MaltConnectTreePreview,
    NODE_OT_MaltAddSubcategoryNode,
]

class MaltNodeDrawCallbacks:

    @staticmethod
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
    
    @staticmethod
    def tree_preview_ui_callback():
        import blf, mathutils
        font_id = 0
        context = bpy.context
        space:bpy.types.SpaceNodeEditor = context.space_data
        if not is_malt_tree_context(context):
            return
        node_tree: MaltTree = space.edit_tree
        tp:NodeTreePreview = node_tree.tree_preview
        socket, identifier = tp.get_socket_ex()
        if socket == None:
            return
        
        preferences = context.preferences
        view2d = context.region.view2d
        label_style = preferences.ui_styles[0].widget_label
        size = label_style.points
        dpifac = preferences.system.dpi * preferences.system.pixel_size / 72
        #calculate the zoom of the view by taking the difference of transformed points in the x-axis
        zoom = (view2d.view_to_region(100 * dpifac, 0, clip=False)[0] - view2d.view_to_region(0, 0, clip=False)[0]) / 100.0

        node = socket.node
        view_loc = node.location
        view_loc = ((view_loc[0] + 5) * dpifac, (view_loc[1] + 5) * dpifac)
        region_loc = mathutils.Vector(view2d.view_to_region(*view_loc, clip=False))
        text = f'Preview: {repr(identifier)}'
        #mix the socket color with white to get a result thats not too dark
        color = (mathutils.Vector(socket.draw_color(context, node)) + mathutils.Vector((1,1,1,1))) * 0.5

        def draw_text(text: str, size: float, loc: tuple[float, float], color: tuple[float, float, float, float]):
            blf.size(0, size, 72)
            blf.position(0, *loc, 0)
            blf.color(0, *color)
            blf.draw(0, text)

        draw_text(text, size * zoom, tuple(region_loc + mathutils.Vector((0,-1))), (0,0,0,1))
        draw_text(text, size * zoom, region_loc, color)

def register_internal_category_toggle(register: bool):
    menu = bpy.types.NODE_PT_overlay
    wm = bpy.types.WindowManager
    attr_name = 'malt_toggle_internal_category'

    def draw_toggle(self:bpy.types.Menu, context: bpy.types.Context):
        self.layout.label(text='Malt')
        self.layout.prop(context.window_manager, attr_name)
    
    if register:
        setattr(wm, attr_name, bpy.props.BoolProperty(name='Show Internal Nodes', default=False))
        menu.append(draw_toggle)
    else:
        delattr(wm, attr_name)
        menu.remove(draw_toggle)


keymaps = []
def register_node_tree_shortcuts():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    def add_shortcut(keymaps: list, operator: bpy.types.Operator, *, type: str, value: str, **modifiers):
        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new(operator.bl_idname, type=type, value=value, **modifiers)
        keymaps.append((km, kmi))

    if kc:
        add_shortcut(keymaps, OT_MaltEditNodeTree, type='TAB', value='PRESS')
        add_shortcut(keymaps, OT_MaltSetTreePreview, type='LEFTMOUSE', value='PRESS', shift=True, alt=True)
        add_shortcut(keymaps, OT_MaltConnectTreePreview, type='LEFTMOUSE', value='PRESS', shift=True, ctrl=True)

def register():
    for _class in classes: bpy.utils.register_class(_class)

    global CONTEXT_PATH_DRAW_HANDLER, TREE_PREVIEW_DRAW_HANDLER
    CONTEXT_PATH_DRAW_HANDLER = bpy.types.SpaceNodeEditor.draw_handler_add(MaltNodeDrawCallbacks.context_path_ui_callback, (), 'WINDOW', 'POST_PIXEL')
    TREE_PREVIEW_DRAW_HANDLER = bpy.types.SpaceNodeEditor.draw_handler_add(MaltNodeDrawCallbacks.tree_preview_ui_callback, (), 'WINDOW', 'POST_PIXEL')

    register_node_tree_shortcuts()

    NodeTree.tree_preview = PointerProperty(type=NodeTreePreview, name='Node Tree Preview',
        options={'LIBRARY_EDITABLE'}, override={'LIBRARY_OVERRIDABLE'})

    register_internal_category_toggle(True)

def unregister():

    register_internal_category_toggle(False)

    del NodeTree.tree_preview

    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
        keymaps.clear()

    global CONTEXT_PATH_DRAW_HANDLER, TREE_PREVIEW_DRAW_HANDLER
    bpy.types.SpaceNodeEditor.draw_handler_remove(CONTEXT_PATH_DRAW_HANDLER, 'WINDOW')
    bpy.types.SpaceNodeEditor.draw_handler_remove(TREE_PREVIEW_DRAW_HANDLER, 'WINDOW')

    for _class in reversed(classes): bpy.utils.unregister_class(_class)