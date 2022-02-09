import bpy

class OT_MaltPrintError(bpy.types.Operator):
    bl_idname = "wm.malt_print_error"
    bl_label = "Print Malt Error"
    bl_description = "MALT ERROR"
    bl_options = {'INTERNAL'}

    message : bpy.props.StringProperty(default="Malt Error", description='Error Message')

    @classmethod
    def description(cls, context, properties):
        return properties.message

    def execute(self, context):
        self.report({'ERROR'}, self.message)
        return {'FINISHED'}
    
    def modal(self, context, event):
        self.report({'ERROR'}, self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

# Always store paths in UNIX format so saved files work across OSs
def malt_path_setter(property_name):
    def setter(self, value):
        self[property_name] = value.replace('\\','/')
    return setter

def malt_path_getter(property_name):
    def getter(self):
        return self.get(property_name,'').replace('\\','/')
    return getter

# Operator buttons are generated every time the UI is redrawn.
# The UI is redrawn for every frame the cursor hovers over it
# The operator button called is not the last one created (???)
# So _MAX_CALLBACKS should be at least (max drawn operator buttons) * (max ui redraws after the button was created)
_MAX_CALLBACKS = 1000
_CALLBACKS = [None] * _MAX_CALLBACKS
_LAST_HANDLE = 0

class MaltCallback(bpy.types.PropertyGroup):

    def set(self, callback, message=''):
        global _CALLBACKS, _LAST_HANDLE, _MAX_CALLBACKS
        _LAST_HANDLE += 1
        _LAST_HANDLE = _LAST_HANDLE % _MAX_CALLBACKS
        _CALLBACKS[_LAST_HANDLE] = callback
        self['_MALT_CALLBACK_'] = _LAST_HANDLE
        self['_MESSAGE_'] = message
    
    def call(self, *args, **kwargs):
        global _CALLBACKS
        _CALLBACKS[self['_MALT_CALLBACK_']](*args, **kwargs)

class OT_MaltCallback(bpy.types.Operator):
    bl_idname = "wm.malt_callback"
    bl_label = "Malt Callback Operator"
    bl_options = {'INTERNAL'}

    callback : bpy.props.PointerProperty(type=MaltCallback)

    @classmethod
    def description(self, context, properties):
        return properties.callback['_MESSAGE_']

    def execute(self, context):
        self.callback.call()
        return {'FINISHED'}

class COMMON_UL_UI_List(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        item.draw(context, layout, data)

def malt_template_list(layout, owner, list_property, index_property, add_callback = None, remove_callback = None):
    row = layout.row()
    row.template_list('COMMON_UL_UI_List', '', owner, list_property, owner, index_property)
    col = row.column()
    list = getattr(owner, list_property)
    index = getattr(owner, index_property)
    col.operator('wm.malt_callback', text='', icon='ADD').callback.set(
        add_callback if add_callback else list.add, 'Add')
    col.operator('wm.malt_callback', text='', icon='REMOVE').callback.set(
        remove_callback if remove_callback else lambda: list.remove(index), 'Remove')


import json

# https://developer.blender.org/T51096
def to_json_rna_path_node_workaround(malt_property_group, path_from_group):
    tree = malt_property_group.id_data
    assert(isinstance(tree, bpy.types.NodeTree))
    for node in tree.nodes:
        if node.malt_parameters.as_pointer() == malt_property_group.as_pointer():
            path = 'nodes["{}"].{}'.format(node.name, path_from_group)
            return json.dumps(('NodeTree', tree.name_full, path))

def to_json_rna_path(prop):
    blend_id = prop.id_data
    id_type = str(blend_id.__class__).split('.')[-1]
    if isinstance(prop.id_data, bpy.types.NodeTree):
        id_type = 'NodeTree'
    id_name = blend_id.name_full
    path = prop.path_from_id()
    return json.dumps((id_type, id_name, path))

def from_json_rna_path(prop):
    id_type, id_name, path = json.loads(prop)
    data_map = {
        'Object' : bpy.data.objects,
        'Mesh' : bpy.data.meshes,
        'Light' : bpy.data.lights,
        'Camera' : bpy.data.cameras,
        'Material' : bpy.data.materials,
        'World': bpy.data.worlds,
        'Scene': bpy.data.scenes,
        'NodeTree' : bpy.data.node_groups
    }
    for class_name, data in data_map.items():
        if class_name in id_type:
            return data[id_name].path_resolve(path)
    return None

classes=[
    OT_MaltPrintError,
    MaltCallback,
    OT_MaltCallback,
    COMMON_UL_UI_List,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)

def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)
