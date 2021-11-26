import bpy

class OT_MaltPrintError(bpy.types.Operator):
    bl_idname = "wm.malt_print_error"
    bl_label = "Print Malt Error"
    bl_description = "MALT ERROR"

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

    def set(self, callback):
        global _CALLBACKS, _LAST_HANDLE, _MAX_CALLBACKS
        _LAST_HANDLE += 1
        _LAST_HANDLE = _LAST_HANDLE % _MAX_CALLBACKS
        _CALLBACKS[_LAST_HANDLE] = callback
        self['_MALT_CALLBACK_'] = _LAST_HANDLE
    
    def call(self):
        global _CALLBACKS
        _CALLBACKS[self['_MALT_CALLBACK_']]()

class OT_MaltCallback(bpy.types.Operator):
    bl_idname = "wm.malt_callback"
    bl_label = "Malt Callback Operator"

    callback : bpy.props.PointerProperty(type=MaltCallback)

    def execute(self, context):
        self.callback.call()
        return {'FINISHED'}
    '''
    def __del__(self):
        global _CALLBACKS, _MAX_CALLBACKS
        _CALLBACKS = [None] * _MAX_CALLBACKS
    '''

classes=[
    OT_MaltPrintError,
    MaltCallback,
    OT_MaltCallback,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)

def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)
