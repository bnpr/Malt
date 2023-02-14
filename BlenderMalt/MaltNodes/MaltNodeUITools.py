import bpy
import string
from typing import Union
from bpy.types import NodeTree
from bpy.props import PointerProperty
from . MaltNodeTree import MaltTree
import blf, gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

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
    return (context.area.ui_type == 'MaltTree' and context.space_data.type == 'NODE_EDITOR' and
        context.space_data.edit_tree is not None)

def is_malt_node_context(context: bpy.types.Context) -> bool:
    return is_malt_tree_context(context) and context.active_node is not None

class OT_MaltEditNodeTree(bpy.types.Operator):
    bl_idname = 'wm.malt_edit_node_tree'
    bl_label = 'Edit Node Tree'
    bl_description = 'Edit the graph of the active group node'

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
    bl_description = 'Set an input socket of the active node as the tree preview socket'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return is_malt_node_context(context)
    
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
    bl_description = 'Connect an output of the active node to the node tree preview socket'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return is_malt_node_context(context)
    
    def execute(self, context):
        node_tree: NodeTree = context.space_data.edit_tree
        node = context.active_node
        if not node:
            return {'CANCELLED'}
        tp: NodeTreePreview = node_tree.tree_preview
        tp.reconnect_node(node)
        context.area.tag_redraw()
        return {'FINISHED'}

class OT_MaltCycleSubCategories(bpy.types.Operator):
    bl_idname = 'wm.malt_cycle_sub_categories'
    bl_label = 'Cycle Subcategories'
    bl_description = 'Cycle the subcategories of the active subcategory node'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return is_malt_node_context(context) and context.active_node.bl_idname == 'MaltFunctionSubCategoryNode'

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        self.node_tree: MaltTree = context.space_data.edit_tree
        self.node_tree.disable_updates = True
        self.node = context.active_node
            
        self.function_enums:list[tuple[str,str,str]] = self.node.get_function_enums(context)
        self.init_function_enum = self.node.function_enum

        self.register_interface(True)
        wm = context.window_manager
        wm.modal_handler_add(self)
        return{'RUNNING_MODAL'}
    
    def register_interface(self, register: bool) -> None:
        space = bpy.types.SpaceNodeEditor
        if register:
            self.reset_ui_lists()
            self.draw_handler = space.draw_handler_add(self.draw_modal_interface, (self,), 'WINDOW', 'POST_PIXEL')
        elif self.draw_handler:
            space.draw_handler_remove(self.draw_handler, 'WINDOW')
            del self.draw_handler
    
    def reset_ui_lists(self):
        '''These lists are being read by the UI callback.'''
        self.prev_enums: list[tuple[str, str, str]] = []
        self.next_enums: list[tuple[str, str, str]] = []

    def cycle_function_enums(self, letter: str, cycle_forward: bool) -> None:
        letter = letter.lower()
        enum_subset = [enum for enum in self.function_enums if enum[1].lower().startswith(letter)]
        if not len(enum_subset):
            return #do nothing if there are no possible function_enums with the given letter

        self.reset_ui_lists()
        new_index = 0 if cycle_forward else len(enum_subset) - 1
        new_function_enum = enum_subset[new_index][0]

        if self.node.function_enum in (enum[0] for enum in enum_subset):
            old_index = next(i for i, enum in enumerate(enum_subset) if enum[0] == self.node.function_enum)
            offset = 1 if cycle_forward else -1
            new_index = (old_index + offset) % len(enum_subset)
            new_function_enum = enum_subset[new_index][0]
        
        self.prev_enums = enum_subset[:new_index]
        self.next_enums = enum_subset[new_index + 1:]
        
        self.node.function_enum = new_function_enum
        self.node.setup_width()

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        context.area.tag_redraw()
        if event.type in ['LEFTMOUSE', 'RET', 'SPACE']:
            return self.execute(context)
        if event.type in ['ESC', 'RIGHTMOUSE'] and event.value == 'PRESS':
            return self.cancel(context)
        if event.type in string.ascii_uppercase and event.value == 'PRESS':
            self.cycle_function_enums(event.type, not event.shift)
            return{'RUNNING_MODAL'}
        
        return{'PASS_THROUGH'}

    def execute(self, context: bpy.types.Context):
        self.node_tree.disable_updates = False
        if self.node.function_enum != self.init_function_enum:
            self.node_tree.update_ext(force_update=True)
        self.register_interface(False)
        context.area.tag_redraw()
        return{'FINISHED'}
    
    def cancel(self, context):
        self.node.function_enum = self.init_function_enum
        self.node_tree.disable_updates = False
        self.register_interface(False)
        context.area.tag_redraw()
        return{'CANCELLED'}
    
    @staticmethod
    def draw_modal_interface(operator: 'OT_MaltCycleSubCategories') -> None:
        context = bpy.context
        node: bpy.types.Node = operator.node
        font_id = 0

        if context.space_data.path[-1].node_tree != node.id_data:
            return

        prefs = context.preferences
        label_style = prefs.ui_styles[0].widget_label
        zoom = MaltNodeDrawCallbacks.get_view_zoom(context)
        dpifac = MaltNodeDrawCallbacks.get_dpifac(context)
        to_region_loc = MaltNodeDrawCallbacks.real_region_loc

        prev_enums = operator.prev_enums
        next_enums = operator.next_enums

        text_spacing = 15.0 * zoom
        has_display_items = any(len(x) for x in (prev_enums, next_enums))
        rect_size = 70 if has_display_items else 40
        rect_size *= zoom

        top_left = to_region_loc(Vector(node.location), context)
        bottom_right = to_region_loc(Vector(node.location) + Vector(node.dimensions) * Vector((1/dpifac, - 1/dpifac)), context)
        m_color = Vector((0.0, 0.0, 0.0, 0.8))
        t_color = Vector((0.0, 0.0, 0.0, 0.0))

        vertices = (
            top_left + Vector((0, rect_size)),         (bottom_right.x, top_left.y + rect_size),
            top_left,                                   (bottom_right.x, top_left.y),

            (top_left.x, bottom_right.y),               bottom_right,
            (top_left.x, bottom_right.y - rect_size),   bottom_right + Vector((0, - rect_size))
        )
        vertex_colors = (
            t_color, t_color,
            m_color, m_color,
            m_color, m_color, 
            t_color, t_color
        )
        indices = (
            (0,1,2), (2,1,3),
            (4,5,6), (6,5,7),
        )

        shader = gpu.shader.from_builtin('2D_SMOOTH_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {'pos': vertices, 'color': vertex_colors}, indices=indices)
        gpu.state.blend_set('ALPHA')
        batch.draw(shader)
        gpu.state.blend_set('NONE')

        blf.size(font_id, label_style.points * zoom, 72)
        blf.color(font_id, 1,1,1,1)

        for i, e in enumerate(reversed(prev_enums)):
            loc = top_left + Vector((text_spacing * 0.5, i * text_spacing + text_spacing * 0.5))
            blf.position(font_id, *loc, 0)
            blf.draw(font_id, e[1])

        for i, e in enumerate(next_enums):
            loc = Vector((top_left.x, bottom_right.y)) + Vector((text_spacing * 0.5, -((i + 1) * text_spacing)))
            blf.position(font_id, *loc, 0)
            blf.draw(font_id, e[1])

class NODE_OT_add_malt_subcategory_node(bpy.types.Operator):
    bl_idname = 'node.add_subcategory_node'
    bl_label = 'Add Malt Subcategory Node'
    bl_description = 'Add a new Malt Subcategory node. Automatically invoke subcategory cycling'
    bl_options = {'UNDO'}

    nodetype: bpy.props.StringProperty(default='MaltFunctionSubCategoryNode')
    settings: bpy.props.StringProperty(default='dict()')

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return is_malt_tree_context(context)

    def execute(self, context: bpy.types.Context):
        for n in context.space_data.edit_tree.nodes:
            n.select = False
        bpy.ops.node.add_node('INVOKE_DEFAULT', type=self.nodetype, use_transform=True)
        node: bpy.types.Node = context.active_node
        from collections import OrderedDict #maybe there is a better solution for this but without an exception will be thrown because the class is not imported
        for k, v in eval(self.settings).items():
            try:
                setattr(node, k, eval(v))
            except:
                print(f'Attribute {repr(k)} could not be set on {repr(node)}')
        if context.preferences.addons['BlenderMalt'].preferences.use_subfunction_cycling:
            bpy.ops.wm.malt_cycle_sub_categories('INVOKE_DEFAULT')
        return{'FINISHED'}


# Blender 3.4 changed the way add_search works and broke NodeItems searches
# See https://developer.blender.org/T103108
# This is a copy of the 3.3 NODE_OT_add_search operator so we can get the functionality back
from bl_operators.node import *
class NODE_OT_malt_add_search(NodeAddOperator, Operator):
    '''Add a node to the active tree'''
    bl_idname = "node.malt_add_search"
    bl_label = "Search and Add Node"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "node_item"

    @classmethod
    def poll(cls, context):
        return is_malt_tree_context(context)

    _enum_item_hack = []

    # Create an enum list from node items
    def node_enum_items(self, context):
        import nodeitems_utils

        enum_items = NODE_OT_malt_add_search._enum_item_hack
        enum_items.clear()

        for index, item in enumerate(nodeitems_utils.node_items_iter(context)):
            if isinstance(item, nodeitems_utils.NodeItem):
                enum_items.append(
                    (str(index),
                     item.label,
                     "",
                     index,
                     ))
        return enum_items

    # Look up the item based on index
    def find_node_item(self, context):
        import nodeitems_utils

        node_item = int(self.node_item)
        for index, item in enumerate(nodeitems_utils.node_items_iter(context)):
            if index == node_item:
                return item
        return None

    node_item: EnumProperty(
        name="Node Type",
        description="Node type",
        items=node_enum_items,
    )

    def execute(self, context):
        item = self.find_node_item(context)

        # no need to keep
        self._enum_item_hack.clear()

        if item:
            # apply settings from the node item
            for setting in item.settings.items():
                ops = self.settings.add()
                ops.name = setting[0]
                ops.value = setting[1]

            self.create_node(context, item.nodetype)

            if self.use_transform:
                bpy.ops.node.translate_attach_remove_on_cancel(
                    'INVOKE_DEFAULT')

            return {'FINISHED'}
        else:
            return {'CANCELLED'}

    def invoke(self, context, event):
        self.store_mouse_cursor(context, event)
        # Delayed execution in the search popup
        context.window_manager.invoke_search_popup(self)
        return {'CANCELLED'}

def draw_malt_add_search_menu(menu, context):
    if context.area.ui_type != 'MaltTree':
        return
    layout = menu.layout
    if is_malt_tree_context(context) == False:
        layout.label(text="No node tree selected", icon='ERROR')
    elif context.space_data.edit_tree.graph_type == '':
        layout.label(text="No node tree type selected", icon='ERROR')
    else:
        row = layout.row()
        row.operator_context = "INVOKE_DEFAULT"
        operator = row.operator("node.malt_add_search", text="Search... (Malt)", icon='VIEW_ZOOM')
        operator.use_transform = True


classes = [
    NodeTreePreview,
    OT_MaltEditNodeTree,
    OT_MaltSetTreePreview,
    OT_MaltConnectTreePreview,
    OT_MaltCycleSubCategories,
    NODE_OT_add_malt_subcategory_node,
    NODE_OT_malt_add_search,
]

class MaltNodeDrawCallbacks:

    @staticmethod
    def get_dpifac(context: bpy.types.Context):
        p = context.preferences
        return p.system.dpi * p.system.pixel_size / 72
    
    @staticmethod
    def real_region_loc(view_location: Vector|tuple|list, context: bpy.types.Context) -> Vector:
        return Vector(
            context.region.view2d.view_to_region(
                *[x * MaltNodeDrawCallbacks.get_dpifac(context) for x in view_location], 
                clip=False
                )
            )
    
    @staticmethod
    def get_view_zoom(context: bpy.types.Context) -> float:
        get_loc = MaltNodeDrawCallbacks.real_region_loc
        return (get_loc((100, 0), context).x - get_loc((0, 0), context).x) / 100.0
    
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
        label_style = preferences.ui_styles[0].widget_label
        size = label_style.points
        #calculate the zoom of the view by taking the difference of transformed points in the x-axis
        zoom = MaltNodeDrawCallbacks.get_view_zoom(context)

        node = socket.node
        view_loc = Vector(node.location) + Vector((5,5))
        region_loc = MaltNodeDrawCallbacks.real_region_loc(view_loc, context)
        text = f'Preview: {repr(identifier)}'
        #mix the socket color with white to get a result thats not too dark
        color = (Vector(socket.draw_color(context, node)) + Vector((1,1,1,1))) * 0.5

        def draw_text(text: str, size: float, loc: tuple[float, float], color: tuple[float, float, float, float]):
            blf.size(font_id, size, 72)
            blf.position(font_id, *loc, 0)
            blf.color(font_id, *color)
            blf.draw(font_id, text)

        draw_text(text, size * zoom, tuple(region_loc + Vector((0,-1))), (0,0,0,1))
        draw_text(text, size * zoom, region_loc, color)

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
    
    bpy.types.NODE_MT_add.prepend(draw_malt_add_search_menu)


def unregister():
    bpy.types.NODE_MT_add.remove(draw_malt_add_search_menu)
    
    del NodeTree.tree_preview

    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
        keymaps.clear()

    global CONTEXT_PATH_DRAW_HANDLER, TREE_PREVIEW_DRAW_HANDLER
    bpy.types.SpaceNodeEditor.draw_handler_remove(CONTEXT_PATH_DRAW_HANDLER, 'WINDOW')
    bpy.types.SpaceNodeEditor.draw_handler_remove(TREE_PREVIEW_DRAW_HANDLER, 'WINDOW')

    for _class in reversed(classes): bpy.utils.unregister_class(_class)
